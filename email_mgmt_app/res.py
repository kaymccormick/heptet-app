import abc
import logging
import sys
from abc import abstractmethod, ABCMeta
from collections import UserDict, OrderedDict
from typing import AnyStr, Type, Any

from interfaces import IResource
from zope.component import IFactory
from zope.component.factory import Factory
from zope.interface import Interface, implementer

import pyramid
from email_mgmt_app.entrypoint import EntryPoint
from email_mgmt_app.interfaces import IMapperInfo
from email_mgmt_app.util import get_entry_point_key
from email_mgmt_app.model.meta import Base
from pyramid.config import Configurator
from pyramid.interfaces import IRequestFactory
from pyramid.request import Request

logger = logging.getLogger(__name__)


class IResourceManager(Interface):
    pass


class ResourceOperationTemplate:
    def __init__(self, name: AnyStr) -> None:
        self._name = name

    @property
    def name(self) -> AnyStr:
        return self._name

    @name.setter
    def name(self, new) -> None:
        self._name = new


# mixin for something that has a request property
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

    def __json__(self, request):
        return {'name': self.name, 'optional': self.optional, 'default': self.default, 'label': self.label}

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


# TODO: should this have entry_point_js ??
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

    def __json__(self, request):
        return {'name': self.name, 'args': self.args}

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


@implementer(IResourceManager)
class ResourceManager:
    """
    ResourceManager class. Provides access to res operations.
    """
    templates = [ResourceOperationTemplate('view'),
                 ResourceOperationTemplate('list'),
                 ResourceOperationTemplate('form'),
                 ]

    def __init__(self, config=None, mapper_key=None, title=None, entity_type=None, node_name=None):
        """

        :param config:
        :param mapper_key:
        :param title:
        :param entity_type:
        :param node_name:
        """
        self._mapper_key = mapper_key
        self._entity_type = entity_type
        self._config = config
        self._ops = []
        self._ops_dict = {}
        self._node_name = node_name
        self._title = title
        self._resource = None

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

    def add_action(self, config: Configurator):
        """
        add_action
        :type config: Configurator
        :param config:
        :return:
        """
        op: ResourceOperation

        reg_view = False
        node_name = self._node_name
        root_resource = config.registry.queryUtility(IResource, 'root_resource')
        assert root_resource is not None and isinstance(root_resource, RootResource), root_resource
        my_parent = root_resource
        assert my_parent is not None
        request = config.registry.queryUtility(IRequestFactory, default=Request)({})
        request.registry = config.registry

        #
        # Populate the root resource dictionary with our
        # { node_name, ContainerResource } pair.
        #
        # ContainerResource is the result of the default factory method
        #
        # Our parent is the "email_mgmt_app.resources" in our
        # app registry. That's the root resource!!

        mapper_wrapper = request.registry.queryUtility(IMapperInfo, self._mapper_key)
        entity_type = mapper_wrapper.mapper_info.entity

        resource = root_resource[node_name] = Resource(
            name=node_name, title=self._title,
            parent=my_parent, entity_type=entity_type
        )
        # implemented = factory.getInterfaces()
        # logger.info("implemented is %s", implemented)
        # assert list(implemented) == [IResource]
        # assert implemented.isOrExtends(IResource)

        assert IResource.providedBy(resource)

        request.context = root_resource[node_name]
        request.root = root_resource
        request.subpath = ()
        request.traversed = (node_name,)

        extra = {'context': type(resource)}

        if entity_type is not None:
            # this is a predicate!
            # sanity check this!!
            extra['entity_type'] = entity_type
            assert issubclass(entity_type, Base)
            # this is not a predicate, but is predicateD on having
            # an entity type
            # extra['mapper_info'] = self.mapper_info

        # config.add_view(view=lambda rs,rr: rs,renderer='json')
        for op in self._ops:
            resource.add_name(op.name)
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
            entry_point = EntryPoint(entry_point_key,
                                     request,
                                     request.registry,
                                     js=op.entry_point_js(request),
                                     # we shouldn't be calling into the "operation" for the entry point
                                     mapper_wrapper=mapper_wrapper,
                                     view_kwargs=view_kwargs)
            generator = (op.view.entry_point_generator_factory())(entry_point, request)
            logger.debug("setting generator to %s", generator)
            entry_point.generator = generator
            config.register_entry_point(entry_point)

            view_kwargs['entry_point'] = entry_point
            # d['decorator'] = view_decorator
            logger.debug("Adding view: %s", view_kwargs)
            config.add_view(**view_kwargs)

            reg_view = True

        if not reg_view:
            logger.warning("No view registered!")
        self._resource = resource

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


@implementer(IResource)
class _Resource:
    """
    Base resource type. Implements functionality common to all resource types.
    """

    #
    def __new__(cls, *args, **kwargs):
        logger.critical("cls,args=%s,kwargs=%s,%s", cls, args, kwargs)
        if cls == Resource:
            count = getattr(cls, "__count__", 0)
            count = count + 1
            clsname = "%s_%04X" % (cls.__name__, count)
            setattr(cls, "__count__", count)
            meta = ResourceMeta(clsname, (cls,), {})
            #logger.critical("meta = %s", meta)
            inst = meta(*args, **kwargs)
            try:
                inst.__init__(*args, **kwargs)
            except:
                ex = sys.exc_info()[1]
                raise ex
            return inst
        try:
            x = super().__new__(cls)
        except:
            ex = sys.exc_info()[1]
            logger.critical(ex)
            #logger.critical("%s", )
            raise ex

        return x
    #
    #     clsname = "%s%04X" % (cls.__name__, getattr(cls, '__count__', 0))
    #     setattr(cls, '__count__', getattr(cls, '__count__', 0) + 1)
    #     logger.warning("name is %s", clsname)
    #     dict__ = sys.modules[cls.__module__].__dict__
    #     #dict__[clsname] = _Resource
    #     t = type(clsname, (_Resource), dict())
    #     assert False, t
        #
        # new__ = type((_Resource), {})
        #
        # logger.warning("__new = %s", new__)
        # return new__(name, parent, title, entity_type)

    def __init__(self,
                 name: AnyStr = None,
                 parent: 'ContainerResource' = None,
                 title: AnyStr = None,
                 entity_type: AnyStr = None) -> None:
        """

        :param mgr: ResourceManager instance
        :param name: The name as appropriate for a resource key. (confusing)
        :param parent: Parent resources.
        :param title: Defaults to name if not given.
        """
        # we dont check anything related to parent
        assert parent is not None or isinstance(self, RootResource), "invalid parent %s or self %s" % (parent, type(self))
        self._title = title
        assert isinstance(name, str), "name must be str type"

        self.__name__ = name

        self.__parent__ = parent
        self._entity_type = entity_type
        self._names = []

    def __conform__(self, iface, default=None):
        if iface == IResource:
            return self

    def attach(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name

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


class ResourceMeta(ABCMeta):
    count = 0

    def __new__(cls, *args, **kwargs):
        logger.critical("meta in new %s %s %s", cls, args, kwargs)
        x = super().__new__(cls, *args, **kwargs)
        logger.critical("meta x = %s", x)
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


class Resource(_Resource, metaclass=ResourceMeta):
    pass


@implementer(IResource)
class ContainerResource(Resource, UserDict):
    """
    Resource containing sub-resources.
    """

    def __init__(self, dict_init=None, **kwargs) -> None:
        # this is the only spot where we call Resource.__init__
        super().__init__(**kwargs)
        self.data = OrderedDict(dict_init or {})

    @property
    def is_container(self) -> bool:
        return True

    def __getitem__(self, key=None):
        if key is None:
            logger.critical("poop")
        logger.debug("querying ContainerResource for %s.%s", self, key)
        v = super().__getitem__(key)
        logger.debug("result is %s", v)
        return v

    def __setitem__(self, key, value):
        logger.debug("setting ContainerResource for %s to %s", key, value)
        super().__setitem__(key, value)


class LeafResource(Resource):
    def __getattr__(self, item):
        raise KeyError


class IRootResource(Interface):
    def get_data():
        pass

    def get_root_resource():
        pass


@implementer(IResource)
class RootResource(ContainerResource):
    """
    The root resource for the pyramid application. This is not the same as the RootFactory.
    """

    def __init__(self, dict_init=None, **kwargs) -> None:
        """
        Initializer for a root resource. This is not a singleton class so it should only be instantiated
        once.
        :param dict_init:
        :param kwargs:
        """

        super().__init__(dict_init, name='', parent=None, **kwargs)

    def get_root_resource(self):
        return self

    def __str__(self):
        return "RootResource"

    def __repr__(self):
        return "RootResource"

    def get_data(self):
        return self.data


class EntityResource():
    def __init__(self, name, entity_type) -> None:
        super().__init__()
        self._name = name
        self._entity_type = entity_type

    @property
    def entity_name(self):
        return self._name


def add_resource_manager(config: Configurator, mgr: ResourceManager):
    logger.debug("in add_resource_manager directive.")
    logger.debug("registering mgr.add_action as action for %s", mgr)
    config.action(None, mgr.add_action(config))


def includeme(config: Configurator):
    factory = Factory(Resource, 'resource',
                      'ResourceFactory', (IResource,))
    config.registry.registerUtility(factory, IFactory, 'resource')

    config.add_directive('add_resource_manager', add_resource_manager)
