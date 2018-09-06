import json
import logging
from typing import Dict

from sqlalchemy import Column

from email_mgmt_app.interfaces import IProcess, IEntryPoint
from pyramid.config import Configurator
from pyramid.path import DottedNameResolver
from pyramid_jinja2 import Environment
from zope.component import adapter
from zope.interface import implementer, Interface

logger = logging.getLogger(__name__)
SettingsType = Dict[str, str]
TemplateEnvironmentType = Environment


class IProcessContext(Interface):
    pass


@implementer(IProcessContext)
class ProcessContext:
    def __init__(self):
        self._settings = None
        self._template_env = None

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, new):
        self._settings = new

    @property
    def template_env(self):
        return self._template_env

    @template_env.setter
    def template_env(self, new):
        self._template_env = new


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
    def __init__(self, ep) -> None:
        """

        :param ep:
        """
        self._ep = ep

    def process(self):
        resolver = DottedNameResolver()
        ep = self._ep
        generator = ep.generator
        assert generator

        js_imports = []
        js_stmts = []
        ready_stmts = []

        if ep.view_kwargs and 'view' in ep.view_kwargs:
            view_arg = ep.view_kwargs['view']
            view = resolver.maybe_resolve(view_arg)
            ep.view = view

            if view.entry_point_generator_factory():
                if generator:
                    js_imports = generator.js_imports()
                    if js_imports:
                        for stmt in js_imports:
                            logger.debug("import: %s", stmt)

                    js_stmts = generator.js_stmts()
                    if js_stmts:
                        for stmt in js_stmts:
                            logger.debug("js: %s", stmt)

                    ready_stmts = generator.ready_stmts()

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
