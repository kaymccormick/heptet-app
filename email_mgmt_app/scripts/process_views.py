import json
import logging
import sys
import traceback

from db_dump.args import argument_parser
from sqlalchemy import inspect
from sqlalchemy.engine.reflection import Inspector
from webtest import TestApp

import email_mgmt_app.webapp_main
from email_mgmt_app.entrypoint import IEntryPoint, IEntryPointGenerator
from email_mgmt_app.mschema import EntryPointSchema
from email_mgmt_app.process import ProcessContext, setup_jsonencoder
from pyramid.paster import get_appsettings, setup_logging
from pyramid.path import DottedNameResolver
from pyramid.registry import Registry
from pyramid.request import Request
from email_mgmt_app.scripts.util import get_request, template_env


def main():
    # deal with parsing args
    parser = argument_parser()
    parser.add_argument('--test-app', '-t', help="Test the application", action="store_true")
    args = parser.parse_args()

    config_uri = args.config_uri
    #settings = args.settings[config_uri]

    # setup_logging ...
    setup_logging(config_uri)

    _logger = logging.getLogger(__name__)

    # get_appsettings
    settings = get_appsettings(config_uri)
    # this sets up the json.JSONENcoder.default
    setup = setup_jsonencoder()
    setup()

    resolver = DottedNameResolver()

    # initialize application
    myapp = email_mgmt_app.webapp_main.wsgi_app(None, **settings)
    registry = myapp.registry  # type: Registry

    # first custom code
    pcontext = ProcessContext(settings=settings,
                              template_env=template_env(),
                              )

    # generate a request
    request = get_request(myapp.request_factory, registry)  # type: Request
    # we need to make this component based TODO
    app_dbsession = registry.email_mgmt_app.dbsession

    # I guess app_dbsession is a 1-tuple with the function
    dbsession = app_dbsession[0](request)

    db = inspect(dbsession.get_bind())  # type: Inspector

    # this is messing up us, kinda
    logger = logging.LoggerAdapter(_logger, extra={
        'entry_point': '',
        'abbrname': _logger.name.split('.')[-1]
    })

    eps = EntryPointSchema(many=True)
    eps2 = []
    entry_points = []
    for key,ep in registry.getUtilitiesFor(IEntryPoint):
        entry_points.append(ep)
        eps2.append(ep.key)

    dump = eps.dump(entry_points)
    with open('entry_points.json', 'w') as f:
        json.dump({ 'list': eps2 }, f)
        f.close()

    test_app = TestApp(myapp)

    entry_point_js_template = pcontext.template_env.get_template('entry_point.js.jinja2')
    failures = []
    for entry_point in entry_points:

        ep = entry_point
        generator = ep.generator
        assert generator
        generator.generate()
        #ep.generate()
        entry_point_key = ep.key
        logger = logging.LoggerAdapter(_logger, extra={
            'entry_point': ep.key,
            'abbrname': _logger.name.split('.')[-1]
        })

        js_imports = []
        js_stmts = []
        extra_js_stmts = []

        if ep.view_kwargs and 'view' in ep.view_kwargs:
            view = resolver.maybe_resolve(ep.view_kwargs['view'])
            ep.view = view

            if view.entry_point_generator_factory():
                new_logger = logging.LoggerAdapter(logger.logger.getChild('entry_point_generator'),
                                                   extra={**logger.extra, 'abbrname': logger.extra[
                                                                                          'abbrname'] + '.entry_point_generator'})
                new_logger.debug("!!! generator = %s", view.entry_point_generator)
                request.view_name = ep.view_kwargs['name']
                generator = view.entry_point_generator_factory()(ep, request, logger=new_logger)

                if generator:
                    js_imports = generator.js_imports()
                    if js_imports:
                        for stmt in js_imports:
                            logger.debug("import: %s", stmt)

                    js_stmts = generator.js_stmts()
                    if js_stmts:
                        for stmt in js_stmts:
                            logger.debug("js: %s", stmt)

                    extra_js_stmts = generator.extra_js_stmts()
                    if extra_js_stmts:
                        for stmt in extra_js_stmts:
                            logger.debug("js: %s", stmt)

        fname = 'src/entry_point/%s.js' % entry_point_key
        logger.info("generating output file %s", fname)

        with open(fname, 'w') as f:
            content = entry_point_js_template.render(
                js_imports=js_imports,
                js_stmts=js_stmts,
                extra_js_stmts=extra_js_stmts,
            )
            # logger.debug("content for %s = %s", entry_point_key, content)
            f.write(content)
            f.close()

        if not ep.view_kwargs:
            continue

        if not args.test_app:
            continue

        uri = '/' + ep.view_kwargs['node_name'] + '/' + ep.view_kwargs['name']

        try:
            if ep.view_kwargs['name'] == 'view':
                params = '?id=1'
                uri = uri + params

            logger.debug("uri = %s", uri)
            resp = test_app.get(uri)
            fname = 'temp/%s.html' % ep.key
            logger.info("Writing output file %s" % fname)
            with open(fname, 'w') as fout:
                fout.write(resp.text)
                fout.close()
        except Exception as ex:
            logger.exception(sys.exc_info()[1])
            traceback.print_exc()
            traceback.print_tb(sys.exc_info()[2])
            # logger.critical("exception: %s", repr(ex))

    logger = None
