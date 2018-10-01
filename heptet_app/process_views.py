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
from heptet_app import get_root, ResourceManagerSchema, EntryPointSchema
from heptet_app.interfaces import IEntryPoint
from heptet_app.process import ProcessViewsConfig
from heptet_app.process import VirtualAssetManager, process_view
from heptet_app.process import setup_jsonencoder, FileAssetManager, ProcessContext, process_views, \
    AbstractAssetManager
from marshmallow import Schema, fields

logger = logging.getLogger()


class CommandContext:

    def __init__(self, config) -> None:
        super().__init__()
        self._config = config

    @property
    def config(self) -> ProcessViewsConfig:
        return self._config

    @config.setter
    def config(self, new: ProcessViewsConfig):
        self._config = new


def cmd_entry_points_json(registry, proc_context, line):
    class EntryPointsSchema(Schema):
        entry_points = fields.Dict()

    s = EntryPointSchema()
    entry_points = list(registry.getUtilitiesFor(IEntryPoint))
    eps = map(lambda x: x[1], entry_points)
    s1 = EntryPointSchema()
    json.dump(s1.dump(eps,many=True), fp=sys.stdout)
    exit(0)
    out = []
    for name, ep in entry_points:
        out.append(s.dump(ep))

    json.dump(out,fp=sys.stdout)


def cmd_process_view(registry, proc_context: ProcessContext, line, *args, **kwargs):
    pr = functools.partial(
        print,

    )
    args = re.split("\s+", line)
    ep_name = args[0]
    pr("Process!")
    ep = registry.getUtility(IEntryPoint, ep_name)

    process_view(registry, proc_context.settings, proc_context, ep)


Commands = dict(process_view=cmd_process_view,
                entry_points_json=cmd_entry_points_json)


def exec_command(registry, proc_context, cmd_line):
    logger.critical(cmd_line)
    cmd_match = re.search(r"^(\S+)\s*", cmd_line)
    cmd = cmd_match.group(1)
    if cmd in Commands:
        f = Commands[cmd]
        span = cmd_match.span()
        f(registry, proc_context, cmd_line[span[1]:])


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
    config = ProcessViewsConfig(output_path=settings['heptet_app.process_views_output_path'])

    # we need to do this automatically
    setup = setup_jsonencoder()
    setup()

    # this has the potential to be sticky because we aren't creating the wsgi app as it would be created at runtime
    # FIXME
    config = Configurator(
        settings=settings,
        root_factory=get_root,
        package="heptet_app",
    )

    config.include('.myapp_config')
#    config.include('heptet_app.model.email_mgmt')
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

    asset_mgr, proc_context, template_env = initialize(args, registry, config, settings)

    # here we get our entry points
    entry_points = list(registry.getUtilitiesFor(IEntryPoint))

    if args.list_entry_points:
        for name, ep in entry_points:
            print(name)
        exit(0)

    # ctx = CommandContext(config)

    if args.cmd:
        for cmd in args.cmd:
            exec_command(registry, proc_context, cmd)
        exit(0)

    if args.pipe:
        _run_pipe(registry, proc_context)

    if args.entry_point:
        for name, ep in entry_points:
            if name == args.entry_point:
                process_views(registry, config, proc_context, [(name, ep)])

        for k, v in asset_mgr.asset_path.items():
            logger.critical("%r = %s", k[0].key, v)

        exit(0)

    # we should be able to remove request and registry?
    process_views(registry, config, proc_context, entry_points)
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
            d[k.key] = "./" + Path(v).as_posix()

        with open("entry_point.json", 'w') as f:
            json.dump(d, fp=f, indent=4, sort_keys=True)
            f.close()


def _run_pipe(registry, proc_context):
    while True:
        line = sys.stdin.readline()
        exec_command(registry, proc_context, line)


def initialize(args, registry, config, settings):
    template_env = registry.queryUtility(IJinja2Environment, 'template-env')
    assert template_env
    # specify path
    asset_mgr: AbstractAssetManager
    if args.virtual_assets:
        asset_mgr = VirtualAssetManager()
    else:
        asset_mgr = FileAssetManager("build/assets", mkdir=True)
    proc_context = ProcessContext(config, template_env, asset_mgr)
    registry.registerUtility(proc_context)
    return asset_mgr, proc_context, template_env
