import json
import logging

import webapp_main
from pyramid.renderers import JSON
from pyramid_tm import explicit_manager
from sqlalchemy import Column, ForeignKey, Table, PrimaryKeyConstraint, inspect
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.orm import Mapper, RelationshipProperty

from model.meta import metadata
from jinja2 import Environment, PackageLoader, select_autoescape
import os
import sys

from pyramid.paster import (
    get_appsettings,
)

from pyramid.scripts.common import parse_vars


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

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

    # FIXME we need to do away with our custom reg key
    env = request.registry.email_mgmt_app.jinja2_env

    for column in mapper.columns:
        cols.append("%s.%s" % (column.table.key, column.key))
        #colren = env.get_template('column.jinja2').render(**coldict)

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



def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    #setup_logging(config_uri)
    logging.basicConfig(level=logging.CRITICAL)
    settings = get_appsettings(config_uri, options=options)



    json_renderer = JSON()
    json_renderer.add_adapter(Mapper, mapper_adapter)
    json_renderer.add_adapter(type, entity_adapter)
    json_renderer.add_adapter(Column, column_adapter)
    json_renderer.add_adapter(ForeignKey, foreignkey_adapter)
    json_renderer.add_adapter(Table, table_adapter)

    json_renderer.add_adapter(PrimaryKeyConstraint, primary_key_constraint_adapter)

    app = webapp_main.main(None, **settings)
    mappers = app.registry.email_mgmt_app.mappers

    request = app.request_factory({})
    request.registry = app.registry
    request.tm = explicit_manager(request)
    dbsession = app.registry.email_mgmt_app.dbsession[0](request)
    db = inspect(dbsession.get_bind()) #type: Inspector

    tables = {}
    for table in db.get_table_names():
        table_o = Table(table, metadata)
        tables[table_o.key] = table_o

    env = Environment(loader=PackageLoader('email_mgmt_app.scripts', 'templates'),
                      autoescape=select_autoescape(default=False))

    #request.registry.email_mgmt_app.jinja2_env = env
    mapper: Mapper
    _m = {}
    for k,mapper in mappers.items():
#        print(json_renderer(None)(mapper, {'request': request}))
        _m[k] = mapper

    #print(json_renderer(None)([EntityView], {'request': request}))

    request.registry.email_mgmt_app.json_renderer = json_renderer
    obj = {'mappers': _m,
                                   'tables': tables,
                                   }
    none_ = json_renderer(None)({ 'mappers': _m,
                                  'tables': tables,
                                  }, {'request': request})
    pp = json.dumps(json.loads(none_), sort_keys=True,
                  indent=4, separators=(',', ': '))
    #pp = jsonpickle.encode(obj)
    print(pp)
    with open('model.json', 'w') as f:
        f.write(pp)
        f.close()






