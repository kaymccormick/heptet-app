import atexit
import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from logging import Formatter

from pyramid.config import Configurator
from pyramid.interfaces import IRendererFactory
from pyramid.paster import get_appsettings, setup_logging
from pyramid.request import Request
from pyramid_jinja2 import IJinja2Environment

import db_dump.args
from email_mgmt_app import get_root, util
import model.email_mgmt
from entrypoint import IEntryPoint, EntryPoints, EntryPoint
from impl import NamespaceStore
from interfaces import IProcess
from myapp_config import on_new_request, TEMPLATE_ENV_NAME
from process import ProcessContext, setup_jsonencoder, AssetManager, GenerateEntryPointProcess
from scripts.util import get_request, template_env

logger = logging.getLogger(__name__)


def main(input_args=None):
    if not input_args:
        input_args = sys.argv[1:]

    logging.lastResort = logging.StreamHandler(stream=sys.stderr)
    logging.lastResort.setFormatter(
        Formatter('%(asctime)s %(levelname)-5.5s [%(name)s:%(lineno)s][%(threadName)s] %(message)s'))

    now = datetime.now()
    logger.debug("Startup in main", now)

    def do_at_exit():
        new_now = datetime.now()
        logger.info("exiting... [%s]", new_now - now)

    atexit.register(do_at_exit)

    # deal with parsing args
    parser = db_dump.args.argument_parser()
    parser.add_argument('--test-app', '-t', help="Test the application", action="store_true")
    args = parser.parse_args(input_args)

    config_uri = args.config_uri

    # setup_logging ...
    setup_logging(config_uri)

    # get_appsettings
    settings = get_appsettings(config_uri)

    setup = setup_jsonencoder()
    setup()

    config = Configurator(settings=settings, root_factory=get_root, package="email_mgmt_app")

    config.include('.myapp_config')
    config.include(model.email_mgmt)
    config.include('.process')

    renderer_pkg = 'pyramid_jinja2.renderer_factory'
    config.add_renderer(None, renderer_pkg)

    config.commit()

    registry = config.registry

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
    request = get_request(Request, registry=registry)  # type: Request
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
    # col_context = CollectorContext(ep_cmp, IEntryPoint)
    # collector = registry.getAdapter(col_context, ICollector)

    eps2 = []
    entry_points = []
    for key, ep in registry.getUtilitiesFor(IEntryPoint):
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
    #    test_app = TestApp(myapp)

    entry_point_js_template = \
        proc_context.template_env.get_template('entry_point.js.jinja2')
    assert entry_points

    root_namespace = NamespaceStore('root')

    ep: EntryPoint
    for ep in entry_points:
        x = repr(ep)
        print(x, file=sys.stderr)
        mi = None
        if ep.mapper_wrapper:
            mi = ep.mapper_wrapper.get_one_mapper_info()

        # fixme this does not belong here!!
        util._dump(registry, cb=lambda fmt, *args: print(fmt % args, file=sys.stderr))
        env = request.registry.getUtility(IJinja2Environment, TEMPLATE_ENV_NAME)
        ep.init_generator(registry, root_namespace, env)
        assert ep.generator is not None
        ep.generator.generate()

        subscribers = registry.subscribers((proc_context, ep), IProcess)
        subscribers = [GenerateEntryPointProcess(proc_context, ep)]
        assert subscribers, "No subscribers for processing"
        for s in subscribers:

            result = s.process()
            if result:
                logger.debug("result = %s", result)

        # for ep in entry_points:
        #     logger.debug("testing entry point %s", ep)
        #
        #     if not ep.view_kwargs:
        #         continue
        #     uri = '/' + ep.view_kwargs['node_name'] + '/' + ep.view_kwargs['name']
        #
        #     try:
        #         if ep.view_kwargs['name'] == 'view':
        #             params = '?id=1'
        #             uri = uri + params
        #
        #         logger.debug("TESTING uri = %s", uri)
        #         resp = test_app.get(uri)
        #         fname = 'temp/%s.html' % ep.key
        #         logger.info("Writing output file %s" % fname)
        #         with open(fname, 'w') as fout:
        #             fout.write(resp.text)
        #             fout.close()
        #     except:
        #         logger.exception(sys.exc_info()[1])
        #         traceback.print_exc()
        #         traceback.print_tb(sys.exc_info()[2])
