from __future__ import annotations
import abc
import inspect
import logging

import sys
from abc import ABCMeta, abstractmethod
from collections import UserDict, OrderedDict
from threading import Lock
from typing import AnyStr, Type

import pyramid
from pyramid.config import Configurator
from pyramid.interfaces import IRequestFactory
from pyramid.request import Request
from sqlalchemy.ext.declarative import DeclarativeMeta
from zope.component import IFactory
from zope.component.factory import Factory
from zope.interface import implementer, Interface

from entrypoint import EntryPoint
from impl import MapperWrapper
from interfaces import IRootResource, IResource
from util import get_entry_point_key

# class MapperInfosMixin:
#     @property
#     def mapper_infos(self) -> dict:
#         return self._mapper_infos
#
#     def get_mapper_info(self, mapper_key: AnyStr) -> MapperInfo:
#         assert mapper_key in self.mapper_infos
#         return self.mapper_infos[mapper_key]
#
#     def set_mapper_info(self, mapper_key: AnyStr, mapper_info: MapperInfo) -> None:
#         self.mapper_infos[mapper_key] = mapper_info


logger = logging.getLogger(__name__)

lock = Lock()


def get_root(request: Request):
    lock.acquire()
    if hasattr(sys.modules[__name__], "_root"):
        root = getattr(sys.modules[__name__], "_root")
        lock.release()
        return root

    root = RootResource()
    setattr(sys.modules[__name__], "_root", root)
    lock.release()
    return root


class ArgumentContext:
    def __init__(self) -> None:
        self._subpath_index = 0

    @property
    def subpath_index(self):
        return self._subpath_index

    @subpath_index.setter
    def subpath_index(self, new):
        logging.info("setting subpath_index to %s", new)
        self._subpath_index = new


class ResourceMeta(ABCMeta):
    count = 0

    def __new__(cls, *args, **kwargs):
        # logger.critical("meta in new %s %s %s", cls, args, kwargs)
        x = super().__new__(cls, *args, **kwargs)
        # logger.critical("meta x = %s", x)
        return x
    # if '__count__' not in cls.__dict__:
    #     setattr(cls, '__count__', 0)
    # dict__ = sys.modules[cls.__module__].__dict__
    # # superclasses = list(superclasses)
    # # superclasses.insert(0, _Resource)
    # # superclasses = tuple(superclasses)
    # #superclasses = list(_Resource, superclasses)
    # clsname = "%s%04X" % (clsname, getattr(cls, '__count__'))
    # setattr(cls, '__count__', getattr(cls, '__count__') + 1)
    # logger.warning("name is %s", clsname)
    # new__ = type.__new__(cls, clsname, superclasses, attributedict)
    # logger.warning("__new = %s", new__)
    # return new__


@implementer(IResource)
class _Resource:
    """
    Base resource type. Implements functionality common to all resource types.
    """

    #
    def __new__(cls, manager, name: AnyStr, parent, *args, **kwargs):
        # logger.critical("cls,args=%s,kwargs=%s,%s", cls, args, kwargs)
        if cls == Resource:
            count = getattr(cls, "__count__", 0)
            count = count + 1
            clsname = "%s_%04X" % (cls.__name__, count)
            setattr(cls, "__count__", count)
            meta = ResourceMeta(clsname, (cls,), {})
            # logger.critical("meta = %s", meta)
            inst = meta(manager, name, parent, *args, **kwargs)
            try:
                inst.__init__(manager, name, parent, *args, **kwargs)
            except:
                ex = sys.exc_info()[1]
                raise ex
            return inst
        try:
            x = super().__new__(cls)
        except:
            ex = sys.exc_info()[1]
            logger.critical(ex)
            # logger.critical("%s", )
            raise ex

        return x

    def __setitem__(self, key, value):
        self._data.__setitem__(key, value)

    def __getitem__(self, k):
        return self._data.__getitem__(k)

    def __len__(self):
        return self._data.__len__()

    def __contains__(self, item):
        return self._data.__contains__(item)

    def __init__(self,
                 name: AnyStr,
                 parent: ContainerResource,
                 manager: ResourceManager,
                 title: AnyStr = None,
                 entity_type: DeclarativeMeta = None,
                 ) -> None:
        """

        :type parent: ContainerResource
        :param name: The name as appropriate for a resource key. (confusing)
        :param parent: Parent resources.
        :param title: Defaults to name if not given.
        :param entity_type: Instance of DeclarativeMeta (a sqlalchemy model type)
        """
        # we dont check anything related to parent
        # assert parent is not None or isinstance(self, RootResource), "invalid parent %s or self %s" % (parent, type(self))
        self._title = title
        self.__name__ = name
        self.__parent__ = parent
        self._entity_type = entity_type
        self._names = []
        self._data = {}
        self.__iter__ = lambda: self._data.__iter__()
        self.clear = lambda: self._data.clear()
        self.items = lambda: self._data.items()
        self.keys = lambda: self._data.keys()
        self.values = lambda: self._data.values()
        self.get = lambda x: self._data.get(x)
        self._manager = manager

        # try:
        #     logger.critical("%s", self.__setitem__)
        #     self['test'] = 1
        #     logger.critical(("%s", self['test']))
        # except:
        #     logger.critical(sys.exc_info()[2])

    @property
    def is_container(self) -> bool:
        return False

    @property
    def title(self):
        return self._title

    @property
    def names(self):
        return self._names

    def path(self):
        return pyramid.threadlocal.get_current_request().resource_path(self)

    def url(self):
        return pyramid.threadlocal.get_current_request().resource_url(self)

    @property
    def entity_type(self):
        return self._entity_type

    def add_name(self, name):
        self._names.append(name)

    def sub_resource(self, name: AnyStr):
        sub = self.__class__.__new__(self.__class__, name, self)
        #        logger.critical("%s", dir(sub))
        self[name] = sub
        return sub

    @property
    def manager(self) -> ResourceManager:
        return self._manager


class Resource(_Resource, metaclass=ResourceMeta):
    pass


@implementer(IResource)
class ContainerResource(Resource, UserDict):
    """
    Resource containing sub-resources.
    """

    def __init__(self, name: AnyStr, parent: ContainerResource, title: AnyStr = None,
                 entity_type: DeclarativeMeta = None) -> None:
        super().__init__(name, parent, title, entity_type)
        self.data = OrderedDict()

    @property
    def is_container(self) -> bool:
        return True

    # def __getitem__(self, key=None):
    #     if key is None:
    #         logger.critical("poop") # ???
    #     logger.debug("querying ContainerResource for %s.%s", self, key)
    #     v = super().__getitem__(key)
    #     logger.debug("result is %s", v)
    #     return v
    #
    # def __setitem__(self, key, value):
    #     logger.debug("setting ContainerResource for %s to %s", key, value)
    #     super().__setitem__(key, value)


@implementer(IRootResource)
class RootResource(Resource):
    def __new__(cls):
        return super().__new__(cls, '', None, None)

    def __init__(self) -> None:
        super().__init__('', None, None)


class IResourceManager(Interface):
    pass


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
            mapper_wrapper: MapperWrapper = None,
    ):
        assert mapper_key, "Mapper key must be provided (%s)." % mapper_key
        self._mapper_key = mapper_key
        self._entity_type = entity_type
        self._ops = []
        self._ops_dict = {}
        self._node_name = node_name
        self._title = title
        self._resource = None
        self._mapper_wrapper = mapper_wrapper
        self._mapper_wrappers = {mapper_key: mapper_wrapper}

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


class ResourceOperation:
    """
    Class encapsulating an operation on a resource
    """

    def entry_point_js(self, request: Request, prefix: AnyStr = ""):
        pass

    def __init__(self, name, view, args, renderer=None) -> None:
        """

        :param name: name of the operation - add, view, etc
        :param view: associated view
        :param renderer: associated renderer
        """
        self._renderer = renderer
        self._args = args
        self._view = view
        self._name = name

    def __str__(self):
        return repr(self.__dict__)

    @property
    def renderer(self):
        return self._renderer

    @property
    def view(self):
        return self._view

    @property
    def name(self):
        return self._name

    @property
    def args(self):
        return self._args


class OperationArgument:
    """
    An argument to an operation.
    """

    @staticmethod
    def SubpathArgument(name: AnyStr, argtype, optional: bool = False, default=None, label=None, implicit_arg=False):
        """
        "Convenience" method to create a subpath-sourced argument.
        :param name:
        :param argtype:
        :param optional:
        :param default:
        :param label:
        :param implicit_arg:
        :return:
        """
        return OperationArgument(name, argtype, optional=optional, default=default, getter=SubpathArgumentGetter(),
                                 label=label, implicit_arg=implicit_arg)

    def __init__(self, name: AnyStr, argtype, optional: bool = False, default=None, getter=None, has_value=None,
                 label=None, implicit_arg=False) -> None:
        """

        :param name:
        :param argtype:
        :param optional:
        :param default:
        :param getter:
        :param has_value:
        :param label:
        :param implicit_arg:
        """
        self._default = default
        self._name = name
        self._argtype = argtype
        self._optional = optional
        self._getter = getter
        self._has_value = has_value
        if label is None:
            self._label = self._name
        else:
            self._label = label

        self._implicit_arg = implicit_arg

    def __str__(self):
        return repr(self.__dict__)

    def __repr__(self):
        return str(self)

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, new):
        self._default = new

    @property
    def name(self) -> AnyStr:
        return self._name

    @property
    def argtype(self):
        return self._argtype

    @property
    def optional(self) -> bool:
        return self._optional

    @property
    def label(self) -> AnyStr:
        return self._label

    @property
    def implicit_arg(self) -> bool:
        return self._implicit_arg

    def get_value(self, request, arg_context):
        if self._getter is not None:
            return self._getter.get_value(self, request, arg_context)

    def has_value(self, request, arg_context):
        if self._has_value is not None:
            return self._has_value(self, request, arg_context)
        return None


class HasRequestMixin:
    @property
    def request(self):
        return self._request

    @request.setter
    def request(self, new):
        self._request = new


class OperationArgumentGetter(metaclass=abc.ABCMeta):
    @abstractmethod
    def get_value(self, arg, request, arg_context):
        pass


class ArgumentGetter(OperationArgumentGetter):
    def get_value(self, arg, request: Request, arg_context):
        return request.params[arg.name]


class SubpathArgumentGetter(OperationArgumentGetter):
    def get_value(self, arg, request, arg_context):
        logger.warning("Getting %s", arg.name)
        val = request.subpath[arg_context.subpath_index]
        arg_context.subpath_index = arg_context.subpath_index + 1
        return val


class LeafResource(Resource):
    def __getattr__(self, item):
        raise KeyError


class EntityResource():
    def __init__(self, name, entity_type) -> None:
        super().__init__()
        self._name = name
        self._entity_type = entity_type

    @property
    def entity_name(self):
        return self._name


def _add_resmgr_action(config: Configurator, manager: ResourceManager):
    """

    :type config: Configurator
    :type manager: ResourceManager
    :param manager: ResourceManager instance
    :param config: Configurator instance
    :return:
    """
    op: ResourceOperation

    # sanity checks
    assert manager._mapper_key, "No mapper key (%s)" % manager._mapper_key

    reg_view = False
    node_name = manager.node_name
    root_resource = get_root(None)
    # assert root_resource is not None and isinstance(root_resource, RootResource), root_resource
    my_parent = root_resource
    assert my_parent is not None
    request = config.registry.queryUtility(IRequestFactory, default=Request)({})
    request.registry = config.registry

    #        env = request.registry.getUtility(IJinja2Environment, 'app_env')

    #
    # Populate the root resource dictionary with our
    # { node_name, ContainerResource } pair.
    #
    # ContainerResource is the result of the default factory method
    #
    # Our parent is the "email_mgmt_app.resources" in our
    # app registry. That's the root resource!!

    mapper_wrapper = manager.mapper_wrappers[manager._mapper_key]
    assert mapper_wrapper, "no mapper wrapper %s in %s" % (manager._mapper_key, manager.mapper_wrappers)
    entity_type = mapper_wrapper.mapper_info.entity

    # our factory now returns dynamic classes - you get a unique class
    # back every time.
    resource = Resource(
        name=node_name, title=manager._title,
        parent=my_parent, entity_type=entity_type,
        manager=manager
    )
    root_resource.__setitem__(node_name, resource)
    assert type(resource) is not Resource

    request.context = resource
    request.root = root_resource
    request.subpath = ()
    request.traversed = (node_name,)

    extra = {'context': type(resource)}

    # this makes a direct mapping between operations, entry points, and views.

    for op in manager._ops:
        resource.add_name(op.name)
        op_resource = resource.sub_resource(op.name)

        d = extra.copy()
        d['operation'] = op
        if op.renderer is not None:
            d['renderer'] = op.renderer

        request.view_name = op.name

        entry_point_key = get_entry_point_key(request, root_resource[node_name], op.name)
        view_kwargs = {'view': op.view,
                       'name': op.name,
                       'node_name': node_name,
                       **d}
        entry_point = EntryPoint(manager, entry_point_key,
                                 request,
                                 request.registry,
                                 js=op.entry_point_js(request),
                                 # we shouldn't be calling into the "operation" for the entry point
                                 mapper_wrapper=mapper_wrapper,
                                 view_kwargs=view_kwargs)
        op_resource.entry_point = entry_point
        # logger.critical("op.view is %s", op.view)
        resource.entry_point = entry_point
        x = op.view(resource, request)
        # generator = config.registry.getMultiAdapter([env, entry_point, x], IEntryPointGenerator)
        # # logger.debug("setting generator to %s", generator)
        # entry_point.generator = generator
        config.register_entry_point(entry_point)

        view_kwargs['entry_point'] = entry_point

        # d['decorator'] = view_decorator
        logger.debug("Adding view: %s", view_kwargs)
        config.add_view(**view_kwargs)

        reg_view = True

    if not reg_view:
        logger.warning("No view registered!")
    manager._resource = resource


def add_resource_manager(config: Configurator, mgr: ResourceManager):
    logger.debug("in add_resource_manager directive.")
    logger.debug("registering mgr.add_action as action for %s", mgr)
    config.action(None, _add_resmgr_action(config, mgr))


def includeme(config: Configurator):
    config.include('..entrypoint')
    factory = Factory(Resource, 'resource',
                      'ResourceFactory', (IResource,))
    config.registry.registerUtility(factory, IFactory, 'resource')

    config.add_directive('add_resource_manager', add_resource_manager)
