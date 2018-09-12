from __future__ import annotations
import logging

import sys
from abc import ABCMeta
from collections import UserDict, OrderedDict
from threading import Lock
from traceback import print_stack
from typing import AnyStr

import pyramid
import stringcase
from pyramid.config import Configurator
from pyramid.interfaces import IRequestFactory
from pyramid.request import Request
from sqlalchemy.ext.declarative import DeclarativeMeta
from zope.component import IFactory
from zope.component.factory import Factory
from zope.interface import implementer

from entrypoint import EntryPoint, ResourceManager, DefaultResourceManager, DefaultEntryPoint, default_manager, \
    default_entry_point
from interfaces import IResource, IRootResource
from manager import ResourceOperation
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
    assert root.entry_point
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
    def __new__(cls, manager, name: AnyStr, parent: ContainerResource,
                entry_point: EntryPoint = None,
                title: AnyStr = None,

                ):
        # logger.critical("cls,args=%s,kwargs=%s,%s", cls, args, kwargs)
        if cls == Resource:
            count = getattr(cls, "__count__", 0)
            count = count + 1
            clsname = "%s_%04X" % (cls.__name__, count)
            setattr(cls, "__count__", count)
            meta = ResourceMeta(clsname, (cls,), {})
            # logger.critical("meta = %s", meta)
            inst = meta(manager, name, parent, entry_point, title)
            assert inst.manager is manager
            # inst.__init__(manager, name, parent, entry_point, title)
            return inst

        logger.critical("super = %r", super)
        x = super().__new__(cls)
        if not title:
            title = stringcase.sentencecase(name)
        else:
            title = title
        x.__init__(manager, name, parent, entry_point, title)
        logger.critical("%r", x)
        return x

    def __setitem__(self, key, value):
        self._data.__setitem__(key, value)

    def __getitem__(self, k):
        return self._data.__getitem__(k)

    def __len__(self):
        return self._data.__len__()

    def __contains__(self, item):
        return self._data.__contains__(item)

    def __init__(self, manager: ResourceManager, name: AnyStr, parent: ContainerResource, entry_point: EntryPoint,
                 title: AnyStr = None) -> None:
        """

        :type manager: ResourceManager
        :type parent: ContainerResource
        :param manager: Manager
        :param name: The name as appropriate for a resource key. (confusing)
        :param parent: Parent resources.
        :param title: Defaults to name if not given.
        """
        # we dont check anything related to parent
        # assert parent is not None or isinstance(self, RootResource), "invalid parent %s or self %s" % (parent, type(self))
        assert entry_point is not None, "Need entry point."
        assert entry_point.key

        assert entry_point.manager is not None
        if not title:
            self._title = stringcase.sentencecase(name)
        else:
            self._title = title
        self.__name__ = name
        self.__parent__ = parent
        self._entry_point = entry_point
        assert entry_point is not None
        self._names = []
        self._data = {}
        self.__iter__ = lambda: self._data.__iter__()
        self.clear = lambda: self._data.clear()
        self.items = lambda: self._data.items()
        self.keys = lambda: self._data.keys()
        self.values = lambda: self._data.values()
        self.get = lambda x: self._data.get(x)
        self._manager = manager
        self._entity_type = manager.entity_type
        self._subresource_type = self.__class__

    def validate(self):
        assert self.manager is not None
        assert self.entry_point is not None
        assert self.__name__
        assert self.__parent__ is not None

    def __repr__(self):
        try:
            return "%s(%r, %r, %s, %r)" % (self.__class__.__name__, self._manager, self.__name__,
                                           self.__parent__ and "%s()" % self.__parent__.__class__.__name__ or None,
                                           self._title)
        except:
            return repr(sys.exc_info()[1])
        # s = ''
        # for x in dir(self):
        #     if x.startswith('_') and not x.startswith('__') and not x.startswith('_abc_') and x != '_data':
        #         s = s + x[1:] + '=' + repr(getattr(self, x)) + ', '
        #
        # return "Resource(%s, %s, %sdata=%r)" % (self.__name__, self.__parent__, s, getattr(self, '_data', None)) #manager=%s, name=%s, parent=%s, title=%s, entity_type=%s)" % (
        #     #self._manager, self.__name__, self.__parent__, self._title, self._entity_type
        #     #)

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

    def sub_resource(self, name: AnyStr, entry_point: EntryPoint, title=None):
        logger.critical("%r", self.__class__)
        assert self.manager
        assert self.entry_point
        if not title:
            title = stringcase.sentencecase(name)
        logger.critical("%s", title)
        sub = self._subresource_type.__new__(self._subresource_type, self.manager, name, self, entry_point, title)
        assert sub.manager is self.manager
        # sub.__init__(self.manager, name, self, )
        #        logger.critical("%s", dir(sub))
        self[name] = sub
        return sub

    @property
    def manager(self) -> ResourceManager:
        return self._manager

    @property
    def entry_point(self) -> EntryPoint:
        return self._entry_point

    @entry_point.setter
    def entry_point(self, new: EntryPoint):
        assert 0
        self._entry_point = new


class Resource(_Resource, metaclass=ResourceMeta):
    pass


@implementer(IResource)
class ContainerResource(Resource, UserDict):
    """
    Resource containing sub-resources.
    """

    def __init__(self, manager: AnyStr, name: ContainerResource, parent: AnyStr,
                 entry_point: DeclarativeMeta = None) -> None:
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


class HasRequestMixin:
    @property
    def request(self):
        return self._request

    @request.setter
    def request(self, new):
        self._request = new


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

    container_entry_point = EntryPoint(manager, manager.mapper_key,
                                       request,
                                       request.registry,

                                       mapper_wrapper=mapper_wrapper)

    # our factory now returns dynamic classes - you get a unique class
    # back every time.
    resource = Resource(
        name=node_name, title=manager._title,
        parent=my_parent,
        manager=manager,
        entry_point=container_entry_point,
    )
    root_resource.__setitem__(node_name, resource)
    assert type(resource) is not Resource

    request.context = resource
    request.root = root_resource
    request.subpath = ()
    request.traversed = (node_name,)

    # this makes a direct mapping between operations, entry points, and views.
    extra = {}

    for op in manager._ops:
        resource.add_name(op.name)

        d = extra.copy()
        d['operation'] = op
        if op.renderer is not None:
            d['renderer'] = op.renderer

        request.view_name = op.name

        entry_point_key = get_entry_point_key(request, root_resource[node_name], op.name)
        d['view'] = op.view
        entry_point = EntryPoint(manager, entry_point_key,
                                 request,
                                 request.registry,
                                 js=op.entry_point_js(request),
                                 # we shouldn't be calling into the "operation" for the entry point
                                 mapper_wrapper=mapper_wrapper,
                                 view_kwargs=d)
        logger.critical("spawning sub resource for op %s, %s", op.name, node_name)
        op_resource = resource.sub_resource(op.name, entry_point)
        d['context'] = type(op_resource)

        # x = op.view(resource, request)

        # generator = config.registry.getMultiAdapter([env, entry_point, x], IEntryPointGenerator)
        # # logger.debug("setting generator to %s", generator)
        # entry_point.generator = generator
        config.register_entry_point(entry_point)

        d['entry_point'] = entry_point

        # d['decorator'] = view_decorator
        logger.debug("Adding view: %s", d)
        config.add_view(**d)

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


@implementer(IRootResource)
class RootResource(Resource):
    def __new__(cls, manager=None, name: AnyStr = '', parent: ContainerResource = None,
                entry_point: EntryPoint = None,
                title: AnyStr = None, ):
        if not manager:
            manager = default_manager()
        if not entry_point:
            entry_point = default_entry_point()
        return super().__new__(cls, manager, name, parent, entry_point, title)

    def __init__(self=None, manager=None, name: AnyStr = '', parent: ContainerResource = None,
                 entry_point: EntryPoint = None,
                 title: AnyStr = None, ) -> None:
        if not manager:
            manager = default_manager()
        if not entry_point:
            entry_point = default_entry_point()
        super().__init__(manager, name, parent, entry_point, title)
        assert self._entry_point is entry_point
        self._subresource_type = Resource

    def validate(self):
        assert self.__name__ == ''
        assert self.__parent__ is None
        assert self.manager is not None

    def __repr__(self):
        return 'RootResource()'
