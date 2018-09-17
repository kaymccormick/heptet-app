import atexit
import logging
import sys
from datetime import datetime
from logging import Formatter

from pyramid.config import Configurator
from pyramid.exceptions import ConfigurationExecutionError
from pyramid.paster import setup_logging, get_appsettings
from pyramid.request import Request
from pyramid_jinja2 import IJinja2Environment

import db_dump.args
import email_mgmt_app.model.email_mgmt
from email_mgmt_app import get_root
from email_mgmt_app.interfaces import IEntryPoint
from email_mgmt_app.process import setup_jsonencoder, AssetManager, ProcessContext, process_views
from test.util import get_request
from email_mgmt_app.util import _dump

logger = logging.getLogger()


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
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)

    # we need to do this automatically
    setup = setup_jsonencoder()
    setup()

    config = Configurator(
        settings=settings,
        root_factory=get_root,
        package="email_mgmt_app",
    )

    config.include('.myapp_config')
    config.include(model.email_mgmt)
    config.include('.process')

    config.add_renderer(None, 'pyramid_jinja2.renderer_factory')

    try:
        config.commit()
    except ConfigurationExecutionError:
        msg = "Application error. Can't commit pyramid configuration. %s" % sys.exc_info()[1]
        logger.critical(msg)
        print(msg, file=sys.stderr)
        import traceback
        traceback.print_tb(sys.exc_info()[2], file=sys.stderr)
        print(sys.exc_info()[1], file=sys.stderr)

        exit(1)
    registry = config.registry

    _dump(
        registry,
        line_prefix="utils: ",
        cb=lambda fmt, *args: logger.critical(fmt, *args),
    )

    template_env = registry.queryUtility(IJinja2Environment, 'template-env')
    assert template_env

    asset_mgr = AssetManager("build/assets", mkdir=True)
    proc_context = ProcessContext(settings, template_env, asset_mgr)
    registry.registerUtility(proc_context)
    l = list(registry.getUtilitiesFor(IEntryPoint))

    # generate a request
    request = get_request(Request, registry=registry)  # type: Request
    assert request

    process_views(registry, template_env, proc_context, l, request)
