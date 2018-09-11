from __future__ import annotations

import abc
import logging
from typing import AnyStr, TypeVar, Generic

from pyramid.config import Configurator

from context import GeneratorContext, FormContext
from tvars import TemplateVars
from zope import interface

from interfaces import *
from impl import MyCollector
from zope.component import adapter
from zope.interface import implementer, Interface

from impl import MapperWrapper

logger = logging.getLogger(__name__)


class IEntryPoints(Interface):
    def get_entry_points():
        pass

    def add_entry_point(entry_point):
        pass


@implementer(IEntryPoints)
class EntryPoints:
    def __init__(self) -> None:
        self._entry_points = []

    def get_entry_points(self):
        return self._entry_points

    def add_entry_point(self, entry_point):
        self._entry_points.append(entry_point)

    def add_value(self, instance):
        self._entry_points.append(instance)


class IEntryPointGenerator(Interface):
    pass


@interface.implementer(IEntryPoint)
class EntryPoint:
    """

    """

    def __init__(
            self,
            manager: 'ResourceManager',
            key: AnyStr,
            request=None,
            registry=None,
            generator=None,
            js=None,
            view_kwargs: dict = None,
            mapper_wrapper: MapperWrapper = None,
            template_name=None,
            template=None,
            output_filename=None
    ) -> None:
        # just to make sure we're sane
        assert isinstance(key, str)
        self._key = key
        self._request = request
        if registry is None and request is not None:
            registry = request.registry
        self._registry = registry
        self._generator = generator
        self._js = js
        self._view_kwargs = view_kwargs  # view coupling !!! FIXME
        self._view = None
        self._mapper_wrapper = mapper_wrapper
        self._template_name = template_name
        self._output_filename = output_filename
        self._template = template
        self._vars = TemplateVars()
        self._manager = manager

    def __repr__(self):
        return "EntryPoint(manager=%r, key=%r, request=%r, registry=%r, generator=%r, \
js=%r, view_kwargs=%r, mapper_wrapper=%r, template_name=%r, template=%r, output_filename=%r)" % (

            self._manager,
            self._key,
            self._request.__class__,
            self._registry.__class__,
            self._generator,
            self._js,
            self._view_kwargs,
            self._mapper_wrapper,
            self._template_name,
            self._template,
            self._output_filename
        )

    def get_template_name(self):
        return self._template_name

    def set_template_name(self, template_name):
        self._template_name = template_name

    def get_key(self):
        return self._key

    def get_output_filename(self):
        return self._output_filename

    def set_output_filename(self, filename):
        self._output_filename = filename

    def get_template(self):
        return self._template

    def set_template(self, template):
        self._template = template

    def init_generator(self, registry, root_namespace, template_env):
        gctx = GeneratorContext(self.mapper_wrapper.get_one_mapper_info(), template_env, TemplateVars(),
                                form_context_factory=FormContext, root_namespace=root_namespace)
        generator = registry.getAdapter(gctx, IEntryPointGenerator)
        self.generator = generator

    def __str__(self):
        return repr(self.__dict__)

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, new):
        self._key = new

    @property
    def js(self):
        return self._js

    @js.setter
    def js(self, new):
        self._js = new

    @property
    def view_kwargs(self) -> dict:
        return self._view_kwargs

    @view_kwargs.setter
    def view_kwargs(self, new: dict):
        self._view_kwargs = new

    @property
    def view(self):
        return self._view

    @view.setter
    def view(self, new):
        self._view = new

    @property
    def mapper_wrapper(self) -> MapperWrapper:
        return self._mapper_wrapper

    @property
    def generator(self):
        return self._generator

    @generator.setter
    def generator(self, new):
        # logger.debug("setting generator to %s", new)
        # import traceback
        # traceback.print_stack(file=sys.stderr)
        self._generator = new

    @property
    def vars(self):
        return self._vars

    @property
    def manager(self) -> 'ResourceManager':
        return self._manager
    # @property
    # def vars(self):


# we get a request, which means we get a registry
@adapter(IEntryPoint, IEntryPointView)
@implementer(IEntryPointGenerator)
class EntryPointGenerator(metaclass=abc.ABCMeta):
    def __init__(self, ctx: GeneratorContext) -> None:
        """

        :param entry_point:
        :param view:
        """
        super().__init__()
        self._ctx = ctx

    @property
    def ctx(self) -> GeneratorContext:
        return self._ctx

    @ctx.setter
    def ctx(self, new: GeneratorContext) -> None:
        self._ctx = new

    @abc.abstractmethod
    def generate(self):
        pass

    def js_stmts(self):
        return []

    def js_imports(self):
        return []


def register_entry_point(config, entry_point: IEntryPoint):
    config.registry.registerUtility(entry_point, IEntryPoint, entry_point.key)


def includeme(config: 'Configurator'):
    def do_action():
        config.registry.registerAdapter(MyCollector, [ICollectorContext], ICollector)

    config.add_directive('register_entry_point', register_entry_point)
    config.action(None, do_action)
