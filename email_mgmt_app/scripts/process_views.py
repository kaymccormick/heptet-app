import atexit
import json
import logging
import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime

import db_dump.args
from pyramid_jinja2 import IJinja2Environment
from webtest import TestApp

import email_mgmt_app.webapp_main
import email_mgmt_app.interfaces
import pyramid.interfaces

from context import GeneratorContext, FormContext
from email_mgmt_app import get_root
from entrypoint import IEntryPoint, ICollector, EntryPoints, EntryPoint, IEntryPointGenerator
from impl import CollectorContext, IProcess, NamespaceStore
from interfaces import IMapperInfo
from process import ProcessContext, setup_jsonencoder, AssetManager, GenerateEntryPointProcess
from scripts.util import get_request, template_env
from webapp_main import on_new_request
from pyramid.paster import get_appsettings, setup_logging
from pyramid.registry import Registry
from pyramid.request import Request
from tvars import TemplateVars

logger = logging.getLogger(__name__)


def main(input_args=None):
    if not input_args:
        input_args = sys.argv[1:]

    now = datetime.now()
    logger.critical("%s Startup in main", now)

    def do_atexit():
        newnow = datetime.now()
        logger.critical("exiting... [%s]", newnow - now)

    atexit.register(do_atexit)
    # deal with parsing args
    parser = db_dump.args.argument_parser()
    parser.add_argument('--test-app', '-t', help="Test the application", action="store_true")
    args = parser.parse_args(input_args)

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
            for k, v in resource.data.items():
                r[k] = dump_resources(v)
        else:
            return resource
        return r

    # generate a request
    request = get_request(myapp.request_factory, myapp)  # type: Request
    assert request
    root = get_root(request)
    assert root is not None

    # for x in registry.registeredAdapters():
    #     if len(x.required) != 3:
    #         continue
    #
    #     (ivc, rq, rs) = x.required
    #     if ivc != pyramid.interfaces.IViewClassifier:
    #         continue
    #
    #     logger.debug("%s", rq)
    #     logger.debug("%s", rs)
    #     #logger.debug("view is %s", x.factory)
    #     orig = getattr(x.factory, "__original_view__", None)
    #     logger.debug("view is %s (%s)", x.factory, orig)

    root_res = dump_resources(root)

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

    env = request.registry.getUtility(IJinja2Environment, 'app_env')
    root_namespace = NamespaceStore('root')

    ep: EntryPoint
    for ep in entry_points:
        x = repr(ep)
        print(x, file=sys.stderr)
        mi = None
        if ep.mapper_wrapper:
            mi = ep.mapper_wrapper.get_one_mapper_info()

        # fixme this does not belong here!!
        ep.init_generator(registry, root_namespace, env)
        assert ep.generator is not None
        ep.generator.generate()
        ep.set_template(entry_point_js_template)
        ep.set_output_filename('src/entry_point/%s.js' % ep.get_key())
        subscribers = registry.subscribers((proc_context,ep), IProcess)
        subscribers = [GenerateEntryPointProcess(proc_context, ep)]
        assert subscribers, "No subscribers for processing"
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
