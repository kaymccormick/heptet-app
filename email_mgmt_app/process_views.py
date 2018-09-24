import argparse
import atexit
import functools
import json
import logging
import re
import sys
from datetime import datetime
from logging import Formatter
from pathlib import PurePath, Path

from pyramid.config import Configurator
from pyramid.exceptions import ConfigurationExecutionError
from pyramid.paster import setup_logging, get_appsettings
from pyramid_jinja2 import IJinja2Environment

import db_dump.args
from email_mgmt_app import get_root
from email_mgmt_app.interfaces import IEntryPoint
from email_mgmt_app.process import VirtualAssetManager
from email_mgmt_app.process import setup_jsonencoder, FileAssetManager, ProcessContext, process_views, \
    AbstractAssetManager

logger = logging.getLogger()


def cmd_process_view(*args, fp, **kwargs):
    pr = functools.partial(
        print,
        file=fp

    )
    pr("Process!")
    pass


cmds = dict(process_view=cmd_process_view)


def exec_command(cmd_line):
    logger.critical(cmd_line)
    cmd_match = re.match("^(\S+)\s*", cmd_line)
    cmd = cmd_match.group(1)
    if cmd in cmds:
        f = cmds[cmd]
        f(fp=sys.stdout)


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
    parser.add_argument('--pipe', action="store_true")
    parser.add_argument('--cmd', action="append")

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

    asset_mgr, proc_context, template_env = initialize(args, registry, settings)

    # here we get our entry points
    entry_points = list(registry.getUtilitiesFor(IEntryPoint))

    if args.list_entry_points:
        for name, ep in entry_points:
            print(name)
        exit(0)

    if args.cmd:
        for cmd in args.cmd:
            exec_command(cmd)
        exit(0)

    if args.pipe:
        _run_pipe()

    if args.entry_point:
        for name, ep in entry_points:
            if name == args.entry_point:
                process_views(registry, proc_context, [(name, ep)])

        for k, v in asset_mgr.asset_path.items():
            logger.critical("%r = %s", k[0].key, v)

        exit(0)

    # we should be able to remove request and registry?
    process_views(registry, proc_context, entry_points)
    d = {}
    v: PurePath
    curdir = PurePath("./")

    if args.virtual_assets:
        vd = {}
        for k, v in asset_mgr.asset_content.items():
            vd[k[0].key] = {'content': v}
            d[k[0].key] = "./" + curdir.joinpath(v).as_posix()
        json.dump(vd, fp=sys.stdout)
    else:
        for k, v in asset_mgr.assets.items():
            d[k[0].key] = "./" + Path(v).as_posix()

        with open("entry_point.json", 'w') as f:
            json.dump(d, fp=f, indent=4, sort_keys=True)
            f.close()


def _run_pipe():
    while True:
        line = sys.stdin.readline()
        exec_command(line)


def initialize(args, registry, settings):
    template_env = registry.queryUtility(IJinja2Environment, 'template-env')
    assert template_env
    # specify path
    asset_mgr: AbstractAssetManager
    if args.virtual_assets:
        asset_mgr = VirtualAssetManager()
    else:
        asset_mgr = FileAssetManager("build/assets", mkdir=True)
    proc_context = ProcessContext(settings, template_env, asset_mgr)
    registry.registerUtility(proc_context)
    return asset_mgr, proc_context, template_env
