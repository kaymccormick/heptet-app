import atexit
import json
import logging
import sys
import traceback
from dataclasses import dataclass, field

import db_dump.args
import pyramid_tm
from sqlalchemy import inspect
from sqlalchemy.engine.reflection import Inspector
from webtest import TestApp

import email_mgmt_app.webapp_main
import zope
from email_mgmt_app.entrypoint import IEntryPoint, ICollector, EntryPoints
from email_mgmt_app.impl import CollectorContext, IProcess
from email_mgmt_app.process import ProcessContext, setup_jsonencoder, AssetManager
from email_mgmt_app.scripts.util import get_request, template_env
from email_mgmt_app.webapp_main import on_new_request
from pyramid.interfaces import IView
from pyramid.paster import get_appsettings, setup_logging
from pyramid.registry import Registry
from pyramid.request import Request
from res import IRootResource, IResource
from root import RootFactory
from sqlalchemy_integration import get_tm_session

logger = logging.getLogger(__name__)


def main():
    def do_atexit():
        logger.critical("exiting...")
    atexit.register(do_atexit)
    # deal with parsing args
    parser = db_dump.args.argument_parser()
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

    manager = AssetManager("build/assets", mkdir=True)
    proc_context = ProcessContext(settings, template_env(), manager)

    registry.registerUtility(proc_context)

    def dump_resources(resource):
        r = {}
        if hasattr(resource, "data"):
            for k,v in resource.data.items():
                r[k] = dump_resources(v)
        else:
            return resource
        return r

    # generate a request
    request = get_request(myapp.request_factory, myapp)  # type: Request
    assert request
    for k,v in registry._utility_registrations.items():
        logger.warn("%s = %s", k,v )
    root = registry.queryUtility(IResource, 'root_resource')
    assert root is not None

    #assert request.root
    root_res = dump_resources(root)
    for node_name, resource in root_res.items():
        logger.warning("%s", resource)

        #assert res.IResource.providedBy(resource)
        # logger.warning("%s", IResource.__bases__)
        # logger.warning("%s", IResource.__sro__)
        # logger.warning("%s", IResource.__iro__)
        logger.warning("%s is %s", node_name, resource)
        res = zope.component.createObject('resource', '', None, '', None)
        adapter = registry.queryMultiAdapter((res, request), IView)
        logger.warning("adapter is %s", adapter)
        assert adapter

    # we need to make this component based TODO
    #    app_dbsession = registry.email_mgmt_app.dbsession

    # this should work with sqlalchemy cookiecutter projects
    session_factory = registry['dbsession_factory']
    dbsession = get_tm_session(session_factory, pyramid_tm.explicit_manager(request))
    # we dont do inspection here
    db = inspect(dbsession.get_bind())  # type: Inspector
    assert db

    # wtf is this
    ep_cmp = EntryPoints()
    col_context = CollectorContext(ep_cmp, IEntryPoint)
    collector = registry.getAdapter(col_context, ICollector)

    eps2 = []
    entry_points = []
    for key, ep in registry.getUtilitiesFor(IEntryPoint):
        collector.add_value(ep)
        entry_points.append(ep)
        eps2.append(ep.key)

    # dump = eps.dump(entry_points)
    with open('entry_points.json', 'w') as f:
        json.dump({'list': eps2}, f)
        f.close()

    @dataclass
    class MyEvent:
        request: Request = field(default_factory=lambda: request)

    event = MyEvent()
    on_new_request(event)
    test_app = TestApp(myapp)

    entry_point_js_template = \
        proc_context.template_env.get_template('entry_point.js.jinja2')
    assert entry_points
    for ep in entry_points:
        generator = ep.generator
        generator.generate()
        ep.set_template(entry_point_js_template)
        ep.set_output_filename('src/entry_point/%s.js' % ep.get_key())
        subscribers = registry.subscribers([ep], IProcess)
        for s in subscribers:
            result = s.process()
            if result:
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
