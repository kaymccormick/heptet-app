import json
import logging
import sys
import traceback
from dataclasses import dataclass, field

from db_dump.args import argument_parser
from sqlalchemy import inspect
from sqlalchemy.engine.reflection import Inspector
from webtest import TestApp
from zope import component
from zope.interface import classImplements

import email_mgmt_app.webapp_main
from email_mgmt_app.entrypoint import IEntryPoint, IEntryPointGenerator, ICollector, IObject, IEntryPoints, EntryPoints
from email_mgmt_app.mschema import EntryPointSchema
from email_mgmt_app.process import ProcessContext, setup_jsonencoder
from email_mgmt_app.impl import CollectorContext, IProcess
from pyramid.paster import get_appsettings, setup_logging
from pyramid.path import DottedNameResolver
from pyramid.registry import Registry
from pyramid.request import Request
from email_mgmt_app.scripts.util import get_request, template_env
from email_mgmt_app.webapp_main import on_new_request

logger = logging.getLogger(__name__)


def main():
    # deal with parsing args
    parser = argument_parser()
    parser.add_argument('--test-app', '-t', help="Test the application", action="store_true")
    args = parser.parse_args()

    config_uri = args.config_uri

    # setup_logging ...
    setup_logging(config_uri)

    # get_appsettings
    settings = get_appsettings(config_uri)
    # this sets up the json.JSONENcoder.default
    setup = setup_jsonencoder()
    setup()

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

    ep_cmp = EntryPoints()
    col_context =  CollectorContext(ep_cmp, IEntryPoint)
    collector = registry.getAdapter(col_context, ICollector)
    #logger.debug("collector is %s", collector)

    # this is a mess
    #eps = EntryPointSchema(many=True)
    eps2 = []
    entry_points = []
    for key,ep in registry.getUtilitiesFor(IEntryPoint):
        collector.add_value(ep)
        entry_points.append(ep)
        eps2.append(ep.key)

    #dump = eps.dump(entry_points)
    with open('entry_points.json', 'w') as f:
        json.dump({ 'list': eps2 }, f)
        f.close()

    @dataclass
    class MyEvent:
        request: Request=field(default_factory=lambda: request)

    event = MyEvent()
    on_new_request(event)
    test_app = TestApp(myapp)

    entry_point_js_template =\
        pcontext.template_env.get_template('entry_point.js.jinja2')
    for ep in entry_points:
        generator = ep.generator
        generator.generate()
        ep.set_template(entry_point_js_template)
        ep.set_output_filename('src/entry_point/%s.js' % ep.get_key())
        subscribers = registry.subscribers([ep], IProcess)
        for s in subscribers:
            result = s.process()
            logger.debug("result = %s", result)

    if args.test_app:
        for ep in entry_points:
            logger.debug("testing entry point %s", ep)

            if not ep.view_kwargs:
                continue
            uri = '/' + ep.view_kwargs['node_name'] + '/' + ep.view_kwargs['name']

            try:
                if ep.view_kwargs['name'] == 'view':
                    params = '?id=1'
                    uri = uri + params

                logger.debug("TESTING uri = %s", uri)
                resp = test_app.get(uri)
                fname = 'temp/%s.html' % ep.key
                logger.info("Writing output file %s" % fname)
                with open(fname, 'w') as fout:
                    fout.write(resp.text)
                    fout.close()
            except:
                logger.exception(sys.exc_info()[1])
                traceback.print_exc()
                traceback.print_tb(sys.exc_info()[2])
