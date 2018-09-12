import abc
import logging
from dataclasses import dataclass
from typing import AnyStr

from zope.component import adapter
from zope.interface import implementer

from exceptions import NamespaceCollision
from interfaces import *
from tvars import TemplateVars

logger = logging.getLogger(__name__)


@implementer(ICollectorContext)
class CollectorContext:
    def __init__(self, backing_var, item_type) -> None:
        self._backing_var = backing_var
        self._item_type = item_type

    def get_backing_var(self):
        return self._backing_var

    def get_item_type(self):
        return self._item_type


@implementer(ITemplateVariable)
class TemplateVariableImpl:
    def __init__(self, **kwargs) -> None:
        self._init = kwargs

    def get_name(self):
        return self._init['name']


@adapter(ITemplateVariable)
@implementer(ICollector)
class CollectorImpl:
    def __init__(self, *args) -> None:
        self._args = args

    def collect(self, *items):
        logger.debug("collecting %s", items)


@implementer(IMapperInfo)
class MapperWrapper:
    def __init__(self, mapper_info) -> None:
        self.mapper_info = mapper_info

    def get_mapper_info(self, key):
        assert key == self.mapper_info.local_table.key
        return self.mapper_info

    def get_one_mapper_info(self):
        return self.mapper_info

    @property
    def key(self):
        return self.mapper_info.local_table.key




# @implementer(INamespaceStore)
# class NamespaceStore(NamespaceEntry):
#     def __init__(self, name) -> None:
#         super().__init__(name)
#         self._namespace = {}
#         self._name = name
#
#     def make_namespace(self, key, namespace):
#         logger.debug("in get_namespace(%s, %s)", key, namespace)
#         if key in self._namespace:
#             raise NamespaceCollision(key, namespace, self._namespace[key])
#
#         self._namespace[key] = { 'key': key, 'namespace': namespace, 'items': {} }
#         return NamespaceStore(key)
#
#     def get_id(self, preferred, bits):
#         assert bits
#         assert self._cur_namespace and self._cur_namespace in self._namespace
#
#         items = self._namespace[self._cur_namespace]['items']
#         o = preferred
#         i = 1
#         while preferred in items:
#             i = i + 1
#             preferred = "%s%d" % (o, i)
#             logger.debug("OMG trying %s", preferred)
#
#         items[preferred] = bits
#         return self.make_global_id(self._cur_namespace, preferred)
#
#     def get_namespace(self, key):
#         return self._namespace[key]
#
#     def has_namespace(self, key):
#         return key in self._namespace
#
#     def make_global_id(self, namespace, id):
#         global_id = "0.%s.%s" % (namespace, id)
#
#         global_.make_namespace(namespace, namespace)
#
#
#         return NamespaceEntry(id)
#

class NamespaceMeta(abc.ABCMeta):
    def __new__(cls, clsname, superclasses, attr_dict):
        new__ = super().__new__(cls, clsname, superclasses, attr_dict)
        return new__


@implementer(INamespaceStore)
class NamespaceStore(TemplateVars, metaclass=NamespaceMeta):
    def __init__(self, name, parent=None) -> None:
        super().__init__()
        self._namespace = {}
        self._name = name
        self._parent = parent
        self._element = None

    def set_element(self, element):
        self._element = element

    def get_element(self):
        return self._element

    def make_namespace(self, key):
        assert '.' not in key and '_' not in key, "Invalid key %s" % key
        logger.debug("in get_namespace(%s)", key)
        element = None
        if key in self._namespace:
            element = self._namespace[key].get_element()
            raise NamespaceCollision(key, element, self._namespace[key])

        v = NamespaceStore(key, parent=self)
        self._namespace[key] = v
        return v

    def get_id(self, *args, **kwargs):
        return self.make_global_id()

    def get_namespace(self, key, create: bool = True):
        if key not in self._namespace and create:
            return self.make_namespace(key)

        return self._namespace[key]

    def has_namespace(self, key):
        return key in self._namespace

    def make_global_id(self):
        x = ""
        if self._parent is not None:
            x = self._parent.make_global_id() + '_'
        return "%s%s" % (x, self._name)

    def get_namespace_data(self):
        return self._namespace

    def __str__(self):
        return str(self.make_global_id())

    @property
    def namespace(self):
        return self._namespace


# @implementer(IHtmlIdStore)
# class HtmlIdStore:
#     def __init__(self):
#         self._ids = {}
#         self._namespace = {}
#
#     def get_id(self, preferred, bits):
#         assert bits
#         if preferred not in self._ids:
#             self._ids[preferred] = bits
#             return preferred
#
#         raise IdTaken(preferred, self._ids)
#         # else:
#         #     assert False
#         #     logger.debug("uh oh! preferred id %s taken", preferred)
#         #     test = '.'.join(bits)
#         #     import re
#         #     test = re.sub('[^A-Za-z\._]', '_', test)
#         #     logger.debug("going to use %s", test)
#         #     return test
#

@adapter(ICollectorContext)
@implementer(ICollector)
class MyCollector:
    def __init__(self, context) -> None:
        self._context = context
        self._value = []

    def add_value(self, instance):
        var = self._context.get_backing_var()
        if var:
            var.add_value(instance)
        else:
            self._value.append(instance)

    def get_value(self):
        var = self._context.get_backing_var()
        if var:
            return var.get_value()
        return self._value

class MixinBase:
    def check_instance(self):
        pass

class TemplateEnvMixin(MixinBase):

    def __init__(self) -> None:
        super().__init__()
        self._template_env = None

    @property
    def template_env(self):
        return self._template_env

    @template_env.setter
    def template_env(self, new):
        self._template_env = new

    def __repr__(self):
        return self._template_env.__repr__()

    def check_instance(self):
        super().check_instance()
        assert self.template_env


class GetTemplateMixin(TemplateEnvMixin):
    def __init__(self) -> None:
        super().__init__()

    def get_template(self, name):
        @dataclass
        class _info:
            name: AnyStr
            package: AnyStr = None

        class _template:
            def __init__(self, template_env, info):
                self.template_env = template_env
                self.info = info

            def render(self, **kwargs):
                x = self.template_env(self.info)
                logger.critical("x = %r", x)
                return x(dict(**kwargs), {})

        return _template(self.template_env, _info(name))


