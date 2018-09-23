import argparse
import atexit
import json
import logging
import sys
from datetime import datetime
from logging import Formatter
from pathlib import PurePath

from pyramid.config import Configurator
from pyramid.exceptions import ConfigurationExecutionError
from pyramid.paster import setup_logging, get_appsettings
from pyramid_jinja2 import IJinja2Environment

import db_dump.args
from email_mgmt_app import get_root
from email_mgmt_app.interfaces import IEntryPoint
from email_mgmt_app.process import setup_jsonencoder, AssetManager, ProcessContext, process_views, process_view, \
    AbstractAssetManager
from email_mgmt_app.util import _dump
from email_mgmt_app.process import VirtualAssetManager

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

    parser = argparse.ArgumentParser(parents=[db_dump.args.argument_parser()])
    parser.add_argument('--test-app', '-t', help="Test the application", action="store_true")
    parser.add_argument('--entry-point', '-e', help="Specify entry point", action="store")
    parser.add_argument('--list-entry-points', '-l', help="List entry points", action="store_true")
    parser.add_argument('--virtual-assets', action="store_true")

    args = parser.parse_args(input_args)

    config_uri = args.config_uri
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)

    # we need to do this automatically
    setup = setup_jsonencoder()
    setup()

    # this has the potential to be sticky because we aren't creating the wsgi app as it would be created at runtime
    # FIXME
    config = Configurator(
        settings=settings,
        root_factory=get_root,
        package="email_mgmt_app",
    )

    config.include('.myapp_config')
    config.include('email_mgmt_app.model.email_mgmt')
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

    # _dump(
    #     registry,
    #     line_prefix="utils: ",
    #     cb=lambda fmt, *args: logger.critical(fmt, *args),
    # )

    template_env = registry.queryUtility(IJinja2Environment, 'template-env')
    assert template_env

    # specify path
    asset_mgr: AbstractAssetManager
    if args.virtual_assets:
        asset_mgr = VirtualAssetManager()
    else:
        asset_mgr = AssetManager("build/assets", mkdir=True)

    proc_context = ProcessContext(settings, template_env, asset_mgr)
    registry.registerUtility(proc_context)

    # here we get our entry points
    l = list(registry.getUtilitiesFor(IEntryPoint))

    if args.list_entry_points:
        for name, ep in l:
            print(name)
        exit(0)

    if args.entry_point:
        for name, ep in l:
            if name == args.entry_point:
                process_views(registry, template_env, proc_context, [(name, ep)])

        for k, v in asset_mgr.asset_path.items():
            logger.critical("%r = %s", k[0].key, v)

        exit(0)


    # we should be able to remove request and registry?
    process_views(registry, template_env, proc_context, l)
    d = {}
    v: PurePath
    curdir = PurePath("./")
    vd = {}
    for k, v in asset_mgr.asset_content.items():
        vd[k[0].key] = { 'content': v }
        d[k[0].key] = "./" + curdir.joinpath(v).as_posix()

    if args.virtual_assets:
        json.dump(vd, fp=sys.stdout)

    with open("entry_point.json", 'w') as f:
        json.dump(d, fp=f, indent=4, sort_keys=True)
        f.close()
