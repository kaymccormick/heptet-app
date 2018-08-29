import json
import logging
import traceback

from pyramid.config.views import ViewDeriverInfo
from pyramid.path import DottedNameResolver
from pyramid.renderers import JSON, RendererHelper
from sqlalchemy.orm.attributes import InstrumentedAttribute
from webtest import TestApp

from email_mgmt_app.adapter import AlchemyAdapter
from email_mgmt_app.info import ColumnInfo
from pyramid_tm import explicit_manager
from sqlalchemy import Column, ForeignKey, Table, PrimaryKeyConstraint, inspect
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.orm import Mapper, RelationshipProperty, ColumnProperty

from email_mgmt_app import RootFactory
from email_mgmt_app.entity.model.meta import metadata
import os
import sys

from pyramid.paster import (
    get_appsettings,
    setup_logging
)
from pyramid.request import Request

from pyramid.scripts.common import parse_vars

import email_mgmt_app

from email_mgmt_app.entrypoint import EntryPoint
from email_mgmt_app.process import ProcessContext, setup_jsonencoder


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

def function_adapter(func, request):
    return repr(func)

def repr_adapter(o, request):
    return repr(o)

def view_deriver_info_adapter(info: ViewDeriverInfo, request):
    o={}
    skip = ('renderer_')
    for x, y in info.options.items():
        if y and x not in skip:
            o[x] = y

    if callable(o['view']):
        o['view'] = repr(o['view'])

    return { 'options': o }

def primary_key_constraint_adapter(pkeyc: PrimaryKeyConstraint, request):
    return { 'name': pkeyc.name,
             '__visit_name__': pkeyc.__visit_name__,
             }

def table_adapter(table: Table, request):
    return { 'visit_name': table.__visit_name__,
             'name': table.name,
             'key': table.key,
             'primary_key': table.primary_key,
             'columns': list(table.columns) }

def foreignkey_adapter(fkey: ForeignKey, request):
    return { 'visit_name': fkey.__visit_name__,
             'column': fkey.column }

def entity_adapter(entity, request):
    return {'kind': 'type', 'data': { 'module': entity.__module__,
                                                  'name': entity.__name__ } }


def column_adapter(column: Column, request):
    coldict = {'name': column.name,
               '__visit_name__': column.__visit_name__,
               'type': [column.type.python_type().__class__.__name__,
                        str(column.type.compile())],
               'key': column.key,
               'foreign_keys': list(column.foreign_keys),
               'table': column.table.key }


    return coldict

def mapper_adapter(mapper: Mapper, request):
    cols = []

    column: Column
    for column in mapper.columns:
        cols.append("%s.%s" % (column.table.key, column.key))

    rels = []
    rel: RelationshipProperty
    for rel in mapper.relationships:
        pairs = []
        for x in rel.local_remote_pairs:
            pairs.append(["%s.%s" % (x[0].table.key, x[0].key), "%s.%s" % (x[1].table.key, x[1].key)])

        y = rel.argument
        if callable(y):
            z = y()
        else:
            z = y.entity

        reldict = {'pairs': pairs,
                   'parent': rel.parent.entity.__name__ ,
                   'argument': z.__name__ ,
                   'info': rel.info }
        rels.append(reldict)

#    template = env.get_template('model.jinja2')
    return {
        'entity': mapper.entity,
        'mapped_table': mapper.mapped_table.key,
        'columns': cols,
        'rels': rels,

    }


def process_attribute(attribute: InstrumentedAttribute):
    if attribute.is_property:
        assert False

    prop = attribute.property
    if isinstance(prop, ColumnProperty):
        i = ColumnInfo(key=prop.key)
        #logger.critical("i2 = %s", i)

    #logger.critical("pop = %s", prop.__class__)


def template_env():
    from jinja2 import Environment, PackageLoader, select_autoescape
    env = Environment(
        loader=PackageLoader('email_mgmt_app', 'templates'),
        autoescape=select_autoescape(default=False)
    )
    return env


def get_request(request_factory, myapp_reg):
    request = request_factory({})
    request.registry = myapp_reg
    request.tm = explicit_manager(request)
    return request


def main(argv=sys.argv):

    # begin arg parsing
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    # end arg parsing: vars=config_uri,options

    # setup_logging ...
    setup_logging(config_uri)

    _logger = logging.getLogger(__name__)

    # get_appsettings
    settings = get_appsettings(config_uri, options=options)

    # Our SQLAlchemy adapter
    adapter = AlchemyAdapter()

    # first custom code
    pcontext = ProcessContext(settings=settings,
                              template_env=template_env(),
                              adapter=adapter)

    # this sets up the json.JSONENcoder.default
    setup = setup_jsonencoder()
    setup()

    resolver = DottedNameResolver()

    # initilialize application
    myapp = email_mgmt_app.main(None, **settings)
    myapp_reg = myapp.registry
    myapp_subreg = myapp_reg.email_mgmt_app

    # generate a request
    request = get_request(myapp.request_factory, myapp_reg) # type: Request

    # this looks weird
    app_dbsession = myapp_reg.email_mgmt_app.dbsession

    dbsession = app_dbsession[0](request)

    db = inspect(dbsession.get_bind()) #type: Inspector

    #myapp_subreg.json_renderer = json_renderer

    tables = {}
    for table in db.get_table_names():
        table_o = Table(table, metadata)
        t = adapter.process_table(table, table_o)

    obj = { 'views': myapp_subreg.views,
            'root':  RootFactory(request) }
    #none_ = json_renderer(None)(obj, {'request': request})
    none_ = ""
#    pp = json.dumps(json.loads(none_), sort_keys=True,
#                  indent=4, separators=(',', ': '))
    #print(pp)
    # with open('views.json', 'w') as f:
    #     f.write(pp)
    #     f.close()

    entry_points = myapp_subreg.entry_points

    with open('entry_points.json', 'w') as f:
        json.dump({'list': list(entry_points.keys())},
                  f)
        f.close()

    mappers = myapp_subreg.mappers
    for mapper_key,mapper in mappers.items():
        m_info = adapter.process_mapper(mapper_key, mapper)

    json_ = adapter.info.to_json()
    with open('adapter.json', 'w') as f:
        f.write(json_)
        f.close()

    #none_ = json_renderer(None)({ 'mappers': mappers,
#                                  'tables': tables,
#                                  }, {'request': request})
#    pp = json.dumps(json.loads(none_), sort_keys=True,
#                  indent=4, separators=(',', ': '))

    # with open('model.json', 'w') as f:
    #     f.write(pp)
    #     f.close()

    # original code follows
    #
    # helper = RendererHelper(name="scripts/templates/entry_point.js.jinja2",
    #                         registry=test_app.registry)
    # for entry_point_key in email_reg.entry_points.keys():
    #     with open('src/entry_point/%s.js' % entry_point_key, 'w') as f:
    #
    #         f.write(helper.render({'entry_point_js': email_reg.entry_points[entry_point_key].js}, {'request': request}))
    #         f.close()

    test_app = TestApp(myapp)


    entry_point_js_template = pcontext.template_env.get_template('entry_point.js.jinja2')
    for entry_point_key in entry_points.keys():
        ep = entry_points[entry_point_key]  # type: EntryPoint
        logger = logging.LoggerAdapter(_logger, extra = {
            'entry_point': entry_point_key,
            'abbrname': _logger.name.split('.')[-1]
        })

        js_imports = []
        if ep.view_kwargs and 'view' in ep.view_kwargs:
            view = resolver.maybe_resolve(ep.view_kwargs['view'])
            ep.view = view

            if view.entry_point_generator:

                new_logger = logging.LoggerAdapter(logger.logger.getChild('entry_point_generator'),
                                                         extra={**logger.extra, 'abbrname': logger.extra['abbrname'] + '.entry_point_generator'})
                new_logger.debug("!!! generator = %s", view.entry_point_generator)
                generator = view.entry_point_generator(ep, None, request, logger=new_logger)


                if generator:
                    js_imports = generator.js_imports()
                    if js_imports:
                        for stmt in js_imports:
                            logger.debug("import: %s", stmt)

                    js_stmts = generator.js_stmts()
                    if js_stmts:
                        for stmt in js_stmts:
                            logger.debug("js: %s", stmt)

        #logger.critical("xx %s", repr(ep.view_kwargs))

        js = ep.js

        with open('src/entry_point/%s.js' % entry_point_key, 'w') as f:
            content = entry_point_js_template.render(
                js_imports=js_imports,
                js_stmts=[],
                extra_js_stmts=[],
            )
            #logger.debug("content for %s = %s", entry_point_key, content)
            f.write(content)
            f.close()


        if not ep.view_kwargs:
            continue

        uri = '/' + ep.view_kwargs['node_name'] + '/' + ep.view_kwargs['name']

        try:
            if ep.view_kwargs['name'] == 'view':
                params = '?id=1'
                uri = uri + params

            logger.debug("uri = %s", uri)
            resp = test_app.get(uri)
            with open('temp/%s.html' % ep.key, 'w') as fout:
                fout.write(resp.text)
                fout.close()
        except Exception as ex:
            traceback.print_exc()
            traceback.print_tb(sys.exc_info()[2])
            #logger.critical("exception: %s", repr(ex))

    logger = None

