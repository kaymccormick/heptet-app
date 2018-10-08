from __future__ import annotations

import abc
import logging
import os
import sys
from abc import ABCMeta, abstractmethod
from threading import Lock
from typing import AnyStr, Generic, TypeVar, Type
from zope import interface

import pyramid
import stringcase
from jinja2 import Environment
from marshmallow import Schema, fields
from pyramid.config import Configurator
from pyramid.request import Request
from zope.component import adapter
from zope.interface import implementer, Interface

import heptet_app
from heptet_app.exceptions import MissingArgumentException
from heptet_app.impl import EntityTypeMixin, TemplateEnvMixin, NamespaceStore
from heptet_app.interfaces import IEntryPoint, IEntryPointGenerator, INamespaceStore
from heptet_app.interfaces import IEntryPointMapperAdapter
from heptet_app.interfaces import IEntryPointView, IResourceManager
from heptet_app.interfaces import IResource
from heptet_app.tvars import TemplateVars
from heptet_app.util import get_exception_entry_point_key

T = TypeVar('T')

logger = logging.getLogger(__name__)

lock = Lock()


def get_root(request: Request = None):
    return _get_root()


def _get_root():
    lock.acquire()
    if hasattr(heptet_app, "_root"):
        root = getattr(sys.modules[__name__], "_root")
        lock.release()
        return root

    # THIS REFERENCES AN ENTRY POINT THAT THEN ISNT FOUND, BECAUSE
    # ITS NOT "REGISTERED"
    root = RootResource(entry_point=EntryPoint('root'))
    assert root.entry_point
    setattr(sys.modules[__name__], "_root", root)
    lock.release()
    return root


def reset_root(request: Request):
    lock.acquire()
    if hasattr(sys.modules[__name__], "_root"):
        delattr(sys.modules[__name__], "_root")
    lock.release()


class AppBase(object):
    pass


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

    def _serialize(cls, field, value, attr, obj):
        return str(type(value))

    def __new__(cls, *args, **kwargs):
        # logger.debug("meta in new %s %s %s", cls, args, kwargs)
        x = super().__new__(cls, *args, **kwargs)
        # logger.debug("meta x = %s", x)
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


class ResourceMagic(AppBase):
    def __setitem__(self, key, value):
        self._data.__setitem__(key, value)

    def __getitem__(self, k):
        if k in ('__parent__', '__name__', '_data', 'manager'):
            raise AttributeError

        return self._data.__getitem__(k)

    def __len__(self):
        return self._data.__len__()

    def __contains__(self, item):
        return self._data.__contains__(item)

    def __format__(self, spec: AnyStr):
        if 'compact' in spec.split(','):
            return self.__class__.__name__
        return super().__format__(spec)

    def __repr__(self):
        try:
            return "%s(%r, %s, %r)" % (self.__class__.__name__, self.__name__,
                                       self.__parent__ and "%s()" % self.__parent__.__class__.__name__ or None,
                                       self._title)
        except:
            return repr(sys.exc_info()[1])


class EntryPointMixin:
    def __init__(self) -> None:
        super().__init__()
        self._entry_point = None  # type: EntryPoint

    @property
    def entry_point(self) -> EntryPoint:
        return self._entry_point

    @entry_point.setter
    def entry_point(self, new: EntryPoint):
        self._entry_point = new


@implementer(IResource)
class _Resource(ResourceMagic, EntityTypeMixin, TemplateEnvMixin, EntryPointMixin):
    """
    Base resource type. Implements functionality common to all resource types.
    """

    def __new__(
            cls,
            name: AnyStr,
            parent: Resource,
            entry_point: EntryPoint,
            title: AnyStr = None,
            template_env=None,
    ):
        """

        :param name:
        :param parent:
        :param entry_point:
        :param title:
        :param template_env:
        :return:
        """
        # fixme not thread safe
        if cls is Resource:
            count = getattr(cls, "__count__", 0)
            count = count + 1
            clsname = "%s_%04X" % (cls.__name__, count)
            setattr(cls, "__count__", count)
            meta = ResourceMeta(clsname, (cls,), {})
            # logger.debug("meta = %s", meta)
            inst = meta(name, parent, entry_point, title, template_env)
            # inst.__init__(manager, name, parent, entry_point, title)
            return inst

        x = super().__new__(cls)
        if not title:
            title = stringcase.sentencecase(name)
        else:
            title = title
        x.__init__(name, parent, entry_point, title, template_env)
        return x

    def __init__(self, name: AnyStr, parent: Resource, entry_point: EntryPoint, title: AnyStr = None,
                 template_env=None) -> None:
        """

        :param name:
        :param parent:
        :param entry_point:
        :param title:
        :param template_env:
        """

        if not title:
            self._title = stringcase.sentencecase(name)
        else:
            self._title = title

        self._template_env = template_env
        self.__name__ = name
        self.__parent__ = parent
        self.entry_point = entry_point

        self._names = []
        self._data = {}
        self.__iter__ = lambda: self._data.__iter__()
        self.clear = lambda: self._data.clear()
        self.items = lambda: self._data.items()
        self.keys = lambda: self._data.keys()
        self.values = lambda: self._data.values()
        self.get = lambda x: self._data.get(x)
        self._entity_type = entry_point and entry_point.manager and entry_point.manager.entity_type
        self._subresource_type = self.__class__

    def validate(self):
        """

        :return:
        """
        assert self.entry_point is not None
        assert self.__name__
        assert self.__parent__ is not None

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

    def url(self, request=None):
        if not request:
            request = pyramid.threadlocal.get_current_request()
        return request.resource_url(self)

    def add_name(self, name):
        self._names.append(name)

    def sub_resource(self, name: AnyStr, entry_point: EntryPoint, title=None):
        logger.debug("%r", self.__class__)
        if not title:
            title = stringcase.sentencecase(name)
        logger.debug("%s", title)
        sub = self._subresource_type.__new__(self._subresource_type, name, self, entry_point, title,
                                             self.template_env)
        self[name] = sub
        return sub


class Resource(_Resource, metaclass=ResourceMeta):
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
            entity_type = None,
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
        # code smell
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
    def operations(self):
        return self._ops

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


# EP-4
# function to add a subtree to the resource tree to represent
# the entity managed by the resource manager.
#
def _add_resmgr_action(config: Configurator, manager: ResourceManager):
    """

    :type config: Configurator
    :type manager: ResourceManager
    :param manager: ResourceManager instance
    :param config: Configurator instance++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    :return:
    """
    op: ResourceOperation

    # sanity checks
    # # MANAGER.MAPPER_KEY
    key = manager.mapper_key
    assert key, "No mapper key (%s)" % key

    reg_view = False
    # # MANAGER.NODE_NAME
    node_name = manager.node_name

    # alter interface to this?
    root_resource = get_root()
    # assert root_resource is not None and isinstance(root_resource, RootResource), root_resource
    my_parent = root_resource
    assert my_parent is not None

    #
    # Populate the root resource dictionary with our
    # { node_name, ContainerResource } pair.
    #
    # ContainerResource is the result of the default factory method
    #
    # Our parent is the "heptet_app.resources" in our
    # app registry. That's the root resource!!

    # can we encapsulate this somehow?
    # MANAGER.MAPPER_WRAPPERS

    # code smell
    mapper_wrapper = manager.mapper_wrappers[key]
    assert mapper_wrapper, "no mapper wrapper %s in %s" % (key, manager.mapper_wrappers)

    # code smell
    container_entry_point = EntryPoint(key, manager, mapper=manager.mapper_wrapper.get_one_mapper_info())
    m = config.registry.getAdapter(container_entry_point, IEntryPointMapperAdapter)
    m.mapper = mapper_wrapper

    resource = Resource(
        name=node_name,
        title=manager.title,
        parent=my_parent,
        entry_point=container_entry_point,
    )
    root_resource.__setitem__(node_name, resource)
    assert type(resource) is not Resource

    # this makes a direct mapping between operations, entry points, and views.
    extra = {}

    # MANAGER.OPERATIONS
    for op in manager.operations:
        resource.add_name(op.name)

        d = extra.copy()
        d['operation'] = op
        if op.renderer is not None:
            d['renderer'] = op.renderer

        entry_point_key = '%s_%s' % (node_name, op.name)
        d['view'] = op.view
        entry_point = EntryPoint(entry_point_key, manager, mapper=mapper_wrapper.get_one_mapper_info())
        logger.debug("spawning sub resource for op %s, %s", op.name, node_name)
        op_resource = resource.sub_resource(op.name, entry_point)
        d['context'] = type(op_resource)

        config.register_entry_point(entry_point)

        d['entry_point'] = entry_point

        # d['decorator'] = view_decorator

        logger.debug("Adding view: %s", d)
        config.add_view(**d)

        reg_view = True

    if not reg_view:
        logger.warning("No view registered!")
    manager._resource = resource


class RootResource(Resource):
    def __new__(cls, name: AnyStr = '', parent: Resource = None,
                entry_point: EntryPoint = None,
                title: AnyStr = None, template_env=None):
        assert entry_point
        return super().__new__(cls, name, parent, entry_point, title, template_env)

    def __init__(self, name: AnyStr = '', parent: Resource = None, entry_point: EntryPoint = None, title: AnyStr = None,
                 template_env=None) -> None:
        assert entry_point
        super().__init__(name, parent, entry_point, title, template_env)
        assert self._entry_point is entry_point
        self._subresource_type = Resource

    def validate(self):
        assert self.__name__ == ''
        assert self.__parent__ is None
        assert self.manager is not None

    def __repr__(self):
        items = self._data.items()
        # use of 'compact' format
        i = map(lambda item: "{0}={1:compact}".format(*item), items)
        x = list(i)
        join = ", ".join(x)
        return 'RootResource(' + join + ')'


class BaseView(Generic[T]):
    def __init__(self, context, request: Request = None) -> None:
        self._context = context
        self._request = request
        self._operation = None
        self._values = {}
        self._entry_point = None
        self._response_dict = {'request': request,
                               'context': context}  # give it a nice default?
        self._template_env = None

    def __call__(self, *args, **kwargs):
        self.collect_args(self.request)
        entry_point = None
        if isinstance(self.context, Exception):
            entry_point = EntryPoint(get_exception_entry_point_key(self.context))
        elif hasattr(self.context, 'entry_point'):
            logger.debug("%s", self.context)
            entry_point = self.context.entry_point

        if entry_point is None:
            assert entry_point is not None, "Entry point for view should not be None (context=%r)" % self.context
        key = entry_point.key
        assert key, "Entry point key for view should be truthy"

        # todo it might be super helpful to sanity check this value, because this generates errors
        # later that t+race to here
        # self._response_dict['entry_point_key'] = entry_point.key
        # self._response_dict['entry_point_template'] = 'build/templates/entry_point/%s.jinja2' % key

        return self._response_dict

    @property
    def request(self) -> Request:
        return self._request

    @request.setter
    def request(self, new: Request) -> None:
        self._request = new

    @property
    def operation(self) -> 'ResourceOperation':
        return self._operation

    @operation.setter
    def operation(self, new) -> None:
        self._operation = new

    def collect_args(self, request):
        if self.operation is None:
            logger.debug("operation is none! this could be bad.")
            return
        assert self.operation is not None
        args = self.operation.args
        values = []
        arg_context = ArgumentContext()
        arg: 'OperationArgument' = None
        for arg in args:
            has_value = arg.has_value(request, arg_context)
            got_value = False
            value = None
            if has_value is None:
                try:
                    value = arg.get_value(request, arg_context)
                    got_value = True
                    has_value = value is not None
                except:
                    logging.info("ex: %s", sys.exc_info()[1])

            if not has_value:
                if arg._default is not None:
                    has_value = True
                    value = arg._default
                    got_value = True

            if not has_value:
                if not arg.optional:
                    raise MissingArgumentException(self.operation, arg, "Missing argument %s for operation %s" % (
                        arg.name, self.operation.name))

            if not got_value:
                value = arg.get_value(request, arg_context)
                got_value = True

            self._values[arg.name] = value
            values.append(value)

    @property
    def entry_point(self):
        return self._entry_point

    @property
    def context(self) -> 'Resource':
        return self._context


class ExceptionView(BaseView):
    def __init__(self, context, request) -> None:
        super().__init__(context, request)
        # request.override_renderer = "templates/exception.jinja2"


class OperationArgumentExceptionView(ExceptionView):
    def __init__(self, context, request) -> None:
        super().__init__(context, request)
        request.override_renderer = "templates/args.jinja2"


#
# SCHEMA
#
class AppBaseSchema(Schema):
    pass


class AssetContentValue(Schema):
    pass


class EntryPointSchema(Schema):
    key = fields.String()
    fspath = fields.Function(lambda ep: ep.__fspath__())
    manager = fields.Nested("ResourceManagerSchema")
    content = fields.String()


class AssetManagerSchema(Schema):
    asset_content = fields.Dict()


class ResourceManagerSchema(Schema):
    mapper_key = fields.String()
    title = fields.String()
    # entity_type = TypeField()
    node_name = fields.String()
    pass


class ResourceSchema(Schema):
    # type = TypeField(attribute='__class__')
    manager = fields.Nested(ResourceManagerSchema)
    name = fields.String(attribute='__name__')  # function=lambda x: x.__name__)
    parent = fields.Nested('self', attribute='__parent__', only=[])  # functiona=lambda x: x.__parent__)
    data = fields.Dict(attribute='_data',
                       keys=fields.String(), values=fields.Nested('ResourceSchema'))
    url = fields.Url(function=lambda x: x.url())


class AssetEntity(AppBase, os.PathLike):
    def __init__(self) -> None:
        super().__init__()


@interface.implementer(IEntryPoint)
class EntryPoint(AssetEntity):
    """
    Encapsulation of an "entry point" to the application; specifically used for javascript entry points
    for bundling purposes (i.e. webpack).
    """

    def __init__(
            self,
            key: AnyStr,
            resource_manager: 'ResourceManager' = None,
            **kwargs,
    ) -> None:
        """
        Initialize the entry point
        :param resource_manager: Associated resource manager
        :param key: dictionary key to identify the entry point
        :param kwargs: other keyword arguments, especially mapper
        """
        super().__init__()
        self._key = key
        self._generator = None
        self._view = None
        # code smell
        self._vars = TemplateVars()
        self._manager = resource_manager
        self._content = None
        for k, v in kwargs.items():
            setattr(self, k, v)

        try:
            x = repr(self)
        except Exception as ex:
            x = ex

        logger.debug("Entry Point is %s", x)

    def __repr__(self):
        """
        Return the value for the repr() of the object
        :return: value for the repr() of the object
        """
        s = "EntryPoint(" + repr(self.key)
        if self.manager:
            s = s + ", manager=%r" % self.manager
        s = s + ")"
        return s

    def __fspath__(self):
        return 'entry_point/%s.js' % self.key

    def init_generator(self, registry, root_namespace, template_env, cb=None, generator_context=None):
        """
        Initiailize the generator?
        :param registry:
        :param root_namespace:
        :param template_env:
        :param cb:
        :param generator_context:
        :return:
        """
        if cb:
            generator = cb(registry, generator_context)
        else:
            generator = registry.getAdapter(generator_context, IEntryPointGenerator)

        return generator

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, new):
        self._key = new

    @property
    def generator(self):
        return self._generator

    @generator.setter
    def set_generator(self, new):
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
        return self.__class__.__name__.lower(), self.key

    @property
    def content(self) -> AnyStr:
        return self._content;

    @content.setter
    def content(self, new: AnyStr):
        self._content = new


class IEntryPoints(Interface):
    pass


@implementer(IEntryPoints)
class EntryPoints:
    def __init__(self) -> None:
        self._entry_points = []

    def add_value(self, instance):
        self._entry_points.append(instance)


class EntryPointConfiguration(dict):
    pass


@adapter(IEntryPoint, IEntryPointView)
@implementer(IEntryPointGenerator)
class EntryPointGenerator(metaclass=abc.ABCMeta):
    def __init__(self, ctx: 'GeneratorContext') -> None:
        """

        :param entry_point:
        :param view:
        """
        super().__init__()
        self._ctx = ctx

    @property
    def ctx(self) -> 'GeneratorContext':
        return self._ctx

    @ctx.setter
    def ctx(self, new: 'GeneratorContext') -> None:
        self._ctx = new

    @abc.abstractmethod
    def generate(self):
        pass

    def js_stmts(self):
        return []

    def js_imports(self):
        return []


TemplateEnvironment = Environment


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


def includeme(config: Configurator):
    config.include('.myapp_config')
    config.include('.view')

    #    renderer_pkg = 'pyramid_jinja2.renderer_factory'
    #    config.add_renderer(None, renderer_pkg)

#    config.include('.routes')

    config.registry.registerUtility(NamespaceStore('form_name'), INamespaceStore, 'form_name')
    config.registry.registerUtility(NamespaceStore('namespace'), INamespaceStore, 'namespace')
