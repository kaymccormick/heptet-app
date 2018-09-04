import abc
import logging
import sys
from typing import AnyStr

from zope import interface

from zope.interface.interfaces import IInterface

from email_mgmt_app.interfaces import *
from jinja2 import Environment
from zope.component import adapter
from zope.interface import implementer, Interface

from email_mgmt_app import MapperInfosMixin
from email_mgmt_app.impl import MapperWrapper
from pyramid_jinja2 import IJinja2Environment

logger = logging.getLogger(__name__)


@adapter(ICollectorContext)
@implementer(ICollector)
class MyCollector:
    def __init__(self, context) -> None:
        self._context = context
        self._value = []

    def add_value(self, instance):
        if self._context._backing_var:
            self._context._backing_var.add_value(instance)
        else:
            self._value.append(instance)

    def get_value(self):
        if self._context._backing_var:
            return self._context._backing_var.get_value()
        return self._value


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

    def __init__(self, key: AnyStr, request=None, registry=None, generator=None, js=None, view_kwargs: dict = None,
                 mapper_wrapper: MapperWrapper = None, template_name=None) -> None:
        """

        :param key:
        :param js:
        :param view:
        """
        assert isinstance(key, str)
        self._key = key
        self._request = request
        if registry is None and request is not None:
            registry = request.registry
        self._registry = registry
        self._generator = generator
        self._js = js
        self._view_kwargs = view_kwargs
        self._view = None
        self._mapper_wrapper = mapper_wrapper
        self._template_name = template_name
        self._output_filename = None
        self._template = None

    def get_template_name(self):
        return self._template_name

    def set_template_name(self, template_name):
        self._template_name = template_name

    def get_key(self):
        return self._key

    def get_output_filename(self):
        return self._output_filename

    def set_output_filename(self, filename):
        self._output_filename =filename

    def get_template(self):
        return self._template

    def set_template(self, template):
        self._template = template

    def __str__(self):
        return repr(self.__dict__)

    def __json__(self, request):
        return self.key

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
    def mapper_wrapper(self):
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


# we get a request, which means we get a registry
@adapter(IEntryPoint)
@implementer(IEntryPointGenerator)
class EntryPointGenerator(MapperInfosMixin):
    def __init__(self, entry_point: EntryPoint, request=None, logger=None) -> None:
        """

        :param entry_point:
        :param context:
        :param request:
        :param logger:
        """
        super().__init__()

        self._entry_point = entry_point
        # TODO we will need to handle more than a single mapper info
        # info = entry_point.operation.resource_manager.mapper_info
        # self._mapper_infos = {}
        # self._mapper_infos[info['mapper_key']] = info
        self._request = request

        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

        #        environment = request.registry.queryUtility(IJinja2Environment, 'app_env')
        #       assert environment
        #      self._template_env = environment
        self._html_id_store = request.registry.queryUtility(IHtmlIdStore)

    @property
    def entry_point(self) -> EntryPoint:
        return self._entry_point

    @property
    def html_id_store(self) -> IHtmlIdStore:
        return self._html_id_store

    def generate(self):
        pass

    def js_stmts(self):
        return []

    def js_imports(self):
        return []

    def extra_js_stmts(self):
        return []


def register_entry_point(config, entry_point: IEntryPoint):
    config.registry.registerUtility(entry_point, IEntryPoint, entry_point.key)


def includeme(config: 'Configurator'):
    def do_action():
        #args = (MyCollector, [IObject], ICollector)
        #logger.debug("registering adapter %s", args)
        #onfig.registry.registerAdapter(*args)
        config.registry.registerAdapter(MyCollector, [ICollectorContext], ICollector)

    config.add_directive('register_entry_point', register_entry_point)
    config.action(None, do_action)
