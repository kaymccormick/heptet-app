import json
import logging
import os
from pathlib import Path

from sqlalchemy import Column

from email_mgmt_app.interfaces import IProcess, IEntryPoint
from pyramid.config import Configurator
from pyramid.path import DottedNameResolver
from zope.component import adapter
from zope.interface import implementer, Interface

logger = logging.getLogger(__name__)


class IProcessContext(Interface):
    pass


@implementer(IProcessContext)
class ProcessContext:
    def __init__(self, settings, template_env, asset_manager):
        self._settings = settings
        self._template_env = template_env
        self._asset_manager = asset_manager

    @property
    def settings(self):
        return self._settings

    @property
    def template_env(self):
        return self._template_env

    @property
    def asset_manager(self):
        return self._asset_manager


class BaseProcessor:
    def __init__(self, pcontext):
        """
        Base class for a processing unit.
        :param pcontext:
        """
        self._pcontex = pcontext

    @property
    def pcontext(self):
        return self._pcontex

    @pcontext.setter
    def pcontext(self, new):
        self._pcontex = new


class AssetManager:
    def __init__(self, output_dir, mkdir=False) -> None:
        super().__init__()
        p = Path(output_dir)
        if p.exists():
            if not p.is_dir():
                raise Exception("%s should be directory." % output_dir)
        else:
            os.mkdir(output_dir)

        self._output_dir = output_dir


    @property
    def output_dir(self):
        return self._output_dir


def setup_jsonencoder():
    def do_setup():
        old_default = json.JSONEncoder.default

        class MyEncoder(json.JSONEncoder):
            def default(self, obj):
                # logging.critical("type = %s", type(obj))
                v = None
                # This is not a mistake.
                if isinstance(obj, Column):
                    return ['Column', obj.name, obj.table.name]

                try:
                    v = old_default(self, obj)
                except:
                    logger.critical("dont know how to jsonify %s", type(obj))
                    # assert False, type(obj)
                    return str(obj)
                return v

        json.JSONEncoder.default = MyEncoder.default

    return do_setup


@adapter(IProcessContext, IEntryPoint)
@implementer(IProcess)
class GenerateEntryPointProcess:
    def __init__(self, context, ep) -> None:
        """

        :param ep:
        """
        self._ep = ep
        self._context = context

    def process(self):
        resolver = DottedNameResolver()
        ep = self._ep

        js_imports = []
        js_stmts = []
        ready_stmts = []

        if ep.view_kwargs and 'view' in ep.view_kwargs:
            view_arg = ep.view_kwargs['view']
            view = resolver.maybe_resolve(view_arg)
            ep.view = view


                # if generator:
                #     js_imports = generator.js_imports()
                #     if js_imports:
                #         for stmt in js_imports:
                #             logger.debug("import: %s", stmt)
                #
                #     js_stmts = generator.js_stmts()
                #     if js_stmts:
                #         for stmt in js_stmts:
                #             logger.debug("js: %s", stmt)
                #
                #     ready_stmts = generator.ready_stmts()

        fname = ep.get_output_filename()
        logger.info("generating output file %s", fname)

        data = {'filename': fname,
                'vars': dict(js_imports=js_imports,

                            js_stmts=js_stmts,
                             ready_stmts=ready_stmts)}

        with open(fname, 'w') as f:
            content = ep.get_template().render(
                **data['vars']
            )
            f.write(content)
            f.close()


def includeme(config: Configurator):
    def do_action():
        config.registry.registerSubscriptionAdapter(GenerateEntryPointProcess)

    config.action(None, do_action)
