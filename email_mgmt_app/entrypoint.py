from __future__ import annotations

import abc
import logging
from typing import AnyStr, Type

from pyramid.config import Configurator
from sqlalchemy.ext.declarative import DeclarativeMeta

from email_mgmt_app.context import GeneratorContext, FormContext
from email_mgmt_app.manager import OperationArgument, ResourceOperation
from email_mgmt_app.tvars import TemplateVars
from zope import interface

from email_mgmt_app.interfaces import *
from email_mgmt_app.impl import Separator
from zope.component import adapter
from zope.interface import implementer, Interface

from email_mgmt_app.impl import MapperWrapper

logger = logging.getLogger(__name__)


def default_entry_point():
    return _default_entry_point


def default_manager():
    return _default_manager


class IEntryPoints(Interface):
    pass


@implementer(IEntryPoints)
class EntryPoints:
    def __init__(self) -> None:
        self._entry_points = []

    def add_value(self, instance):
        self._entry_points.append(instance)


@interface.implementer(IEntryPoint)
class EntryPoint:
    """

    """

    def __init__(
            self,
            manager: 'ResourceManager',
            key: AnyStr,
            generator=None,
            js=None,
            view_kwargs: dict = None,
            mapper_wrapper: MapperWrapper = None,
    ) -> None:
        # just to make sure we're sane
        assert isinstance(key, str)
        self._key = key
        self._generator = generator
        self._js = js
        self._view_kwargs = view_kwargs  # view coupling !!! FIXME
        self._view = None
        self._mapper_wrapper = mapper_wrapper
        self._vars = TemplateVars()
        self._manager = manager
        try:
            x = repr(self)
        except Exception as ex:
            x = ex

        logger.debug("Entry Point is %s", x)

    def __repr__(self):
        return "EntryPoint(manager=%r, key=%r, generator=%r, \
js=%r, view_kwargs=%r, mapper_wrapper=%r)" % (
            self._manager,
            self._key,
            self._generator,
            self._js,
            self._view_kwargs,
            self._mapper_wrapper,

        )

    ## Fix me - this is fragile. inject dependency
    def init_generator(self, registry, root_namespace, template_env, cb=None):
        w = self.mapper_wrapper and self.mapper_wrapper.get_one_mapper_info() or None
        gctx = GeneratorContext(w, TemplateVars(), form_context_factory=FormContext, root_namespace=root_namespace,
                                template_env=template_env)
        if cb:
            generator = cb(registry, gctx)
        else:
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

    @property
    def discriminator(self):
        return [self.__class__.__name__.lower(), Separator, self.key]


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


@implementer(IResourceManager)
class ResourceManager:
    """
    ResourceManager class. Provides access to res operations.
    """

    # templates = [ResourceOperationTemplate('view'),
    #              ResourceOperationTemplate('list'),
    #              ResourceOperationTemplate('form'),
    #              ]

    def __init__(
            self,
            mapper_key: AnyStr = None,
            title: AnyStr = None,
            entity_type: DeclarativeMeta = None,
            node_name: AnyStr = None,
            mapper_wrapper: 'MapperWrapper' = None,
            operation_factory=None,
    ):
        """

        :param mapper_key:
        :param title:
        :param entity_type:
        :param node_name:
        :param mapper_wrapper:
        :param operation_factory:
        """
        assert mapper_key, "Mapper key must be provided (%s)." % mapper_key
        self._operation_factory = operation_factory
        self._mapper_key = mapper_key
        self._entity_type = entity_type
        self._ops = []
        self._ops_dict = {}
        self._node_name = node_name
        self._title = title
        self._resource = None
        self._mapper_wrapper = mapper_wrapper
        self._mapper_wrappers = {mapper_key: mapper_wrapper}

    def __repr__(self):
        return 'ResourceManager(mapper_key=%s, title=%s, entity_type%s, node_name=%s, mapper_wrapper=%s)' % (
            self._mapper_key, self._title, self._entity_type, self._node_name, self._mapper_wrapper
        )

    def operation(self, name, view, args, renderer=None) -> None:
        """
        Add operation to res manager.
        :param name:
        :param view:
        :param renderer:
        :return:
        """
        args[0:0] = self.implicit_args()
        op = ResourceOperation(name=name, view=view, args=args, renderer=renderer)
        self._ops.append(op)
        self._ops_dict[op.name] = op

    def implicit_args(self):
        args = []
        if self._entity_type is not None:
            args.append(OperationArgument('entity_view', Type, default=self._entity_type,
                                          label='Entity Type', implicit_arg=True))
        return args

    @property
    def ops(self) -> dict:
        return self._ops_dict

    @property
    def entity_type(self):
        return self._entity_type

    @property
    def title(self):
        return self._title

    @property
    def resource(self) -> 'Resource':
        return self._resource

    @property
    def mapper_wrappers(self):
        return self._mapper_wrappers

    @property
    def mapper_wrapper(self):
        return self._mapper_wrapper

    @property
    def node_name(self) -> AnyStr:
        return self._node_name

    @property
    def mapper_key(self) -> AnyStr:
        return self._mapper_key


class DefaultResourceManager(ResourceManager):
    def __init__(self):
        super().__init__('_default', '_default', None, '_default', None)


class DefaultEntryPoint(EntryPoint):

    def __init__(self, manager):
        key = "_default"
        registry = None
        generator = None
        js = None
        view_kwargs = {}
        mapper_wrapper = None
        request = None
        super().__init__(manager, key, generator, js, view_kwargs, mapper_wrapper)


_default_manager = DefaultResourceManager()
_default_entry_point = DefaultEntryPoint(_default_manager)


def register_entry_point(config, entry_point: IEntryPoint):
    config.registry.registerUtility(entry_point, IEntryPoint, entry_point.key)


def includeme(config: 'Configurator'):
    def do_action():
        pass
        #config.registry.registerAdapter(MyCollector, [ICollectorContext], ICollector)

    # FIXME rethink this directive?
    config.add_directive('register_entry_point', register_entry_point)
    register_entry_point(config, default_entry_point())
    config.action(None, do_action)
