import abc
import logging
from abc import ABCMeta
from typing import Generic, TypeVar, AnyStr
try:
    from typing import GenericMeta
except ImportError:
    class GenericMeta(type): pass

from zope.component import adapter
from zope.interface import implementer

from heptet_app.exceptions import NamespaceCollision
from heptet_app.interfaces import ITemplateVariable, ICollector, IMapperInfo, INamespaceStore
from heptet_app.tvars import TemplateVars

logger = logging.getLogger(__name__)

T = TypeVar('T')


# @implementer(ICollectorContext)
# class CollectorContext:
#     def __init__(self, backing_var, item_type) -> None:
#         self._backing_var = backing_var
#         self._item_type = item_type
#
#     def get_backing_var(self):
#         return self._backing_var
#
#     def get_item_type(self):
#         return self._item_type


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


NamespaceMetabase = ABCMeta

class NamespaceMeta(NamespaceMetabase):
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

    def __repr__(self):
        return 'NamespaceStore(%s)' % self._name

    @property
    def element(self):
        return self._element

    @element.setter
    def element(self, new):
        self.new = new

    def check_key(self, key: AnyStr):
        assert '.' not in key and '_' not in key, "Invalid key %s" % key
        return True

    def make_namespace(self, key):
        assert self.check_key(key)
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
        # assert self.template_env


class EntityTypeMixin(Generic[T], MixinBase):
    def __init__(self) -> None:
        super().__init__()
        self._entity_type = None  # type: T

    @property
    def entity_type(self) -> T:
        return self._entity_type

    @entity_type.setter
    def entity_type(self, new: T) -> None:
        self._entity_type = new


class _Separator:
    @property
    def discriminator(self):
        return ['/']


Separator = _Separator()
