from __future__ import annotations

import logging
import sys
from abc import ABCMeta
from threading import Lock
from typing import AnyStr, Generic, TypeVar

import pyramid
import stringcase
from pyramid.config import Configurator
from pyramid.interfaces import IRequestFactory
from pyramid.request import Request
from zope.interface import implementer

from db_dump import TypeField
from entrypoint import EntryPoint, ResourceManager, default_manager, \
    default_entry_point
from exceptions import MissingArgumentException
from impl import EntityTypeMixin, TemplateEnvMixin
from interfaces import IResource
from manager import ResourceOperation
from marshmallow import Schema, fields
from mixin import EntryPointMixin
from util import get_entry_point_key, get_exception_entry_point_key

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
T = TypeVar('T')

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


def reset_root(request: Request):
    lock.acquire()
    if hasattr(sys.modules[__name__], "_root"):
        delattr(sys.modules[__name__], "_root")
    lock.release()


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


@implementer(IResource)
class _Resource(EntityTypeMixin, TemplateEnvMixin, EntryPointMixin):
    """
    Base resource type. Implements functionality common to all resource types.
    """

    def __format__(self, spec: AnyStr):
        if spec == 'x':
            return self.__class__.__name__
        return super().__format__(spec)

    def __new__(
            cls,
            name: AnyStr,
            parent: Resource,
            entry_point: EntryPoint,
            title: AnyStr = None,
            template_env=None,
    ):
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

    def __init__(self, name: AnyStr, parent: Resource, entry_point: EntryPoint, title: AnyStr = None,
                 template_env=None) -> None:
        """

        :type parent: ContainerResource
        :param name: The name as appropriate for a resource key. (confusing)
        :param parent: Parent resources.
        :param title: Defaults to name if not given.
        """
        # we dont check anything related to parent
        # assert parent is not None or isinstance(self, RootResource), "invalid parent %s or self %s" % (parent, type(self))
        assert entry_point is not None, "Need entry point."
        assert entry_point.key

        if not title:
            self._title = stringcase.sentencecase(name)
        else:
            self._title = title

        self._template_env = template_env
        self.__name__ = name
        self.__parent__ = parent
        self.entry_point = entry_point
        assert entry_point is not None
        self._names = []
        self._data = {}
        self.__iter__ = lambda: self._data.__iter__()
        self.clear = lambda: self._data.clear()
        self.items = lambda: self._data.items()
        self.keys = lambda: self._data.keys()
        self.values = lambda: self._data.values()
        self.get = lambda x: self._data.get(x)
        self._entity_type = entry_point.manager.entity_type
        self._subresource_type = self.__class__

    def validate(self):
        assert self.entry_point is not None
        assert self.__name__
        assert self.__parent__ is not None

    def __repr__(self):
        try:
            return "%s(%r, %s, %r)" % (self.__class__.__name__, self.__name__,
                                       self.__parent__ and "%s()" % self.__parent__.__class__.__name__ or None,
                                       self._title)
        except:
            return repr(sys.exc_info()[1])

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
        assert self.entry_point
        if not title:
            title = stringcase.sentencecase(name)
        logger.debug("%s", title)
        sub = self._subresource_type.__new__(self._subresource_type, name, self, entry_point, title,
                                             self.template_env)
        self[name] = sub
        return sub


class Resource(_Resource, metaclass=ResourceMeta):
    pass


class HasRequestMixin:
    @property
    def request(self):
        return self._request

    @request.setter
    def request(self, new):
        self._request = new


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
    request = config.registry.queryUtility(IRequestFactory, default=Request)({})
    request.registry = config.registry
    root_resource = get_root(request)
    # assert root_resource is not None and isinstance(root_resource, RootResource), root_resource
    my_parent = root_resource
    assert my_parent is not None

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
    # entity_type = mapper_wrapper.mapper_info.entity

    container_entry_point = EntryPoint(manager, manager.mapper_key,
                                       request,
                                       request.registry,

                                       mapper_wrapper=mapper_wrapper)

    # our factory now returns dynamic classes - you get a unique class
    # back every time.
    resource = Resource(
        name=node_name, title=manager._title,
        parent=my_parent,
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
        if not entry_point:
            entry_point = default_entry_point()
        return super().__new__(cls, name, parent, entry_point, title, template_env)

    def __init__(self, name: AnyStr='', parent: Resource=None, entry_point: EntryPoint=None, title: AnyStr = None,
                 template_env=None) -> None:
        if not entry_point:
            entry_point = default_entry_point()
        super().__init__(name, parent, entry_point, title, template_env)
        assert self._entry_point is entry_point
        self._subresource_type = Resource

    def validate(self):
        assert self.__name__ == ''
        assert self.__parent__ is None
        assert self.manager is not None

    def __repr__(self):

        items = self._data.items()
        i = map(lambda item: "{0}={1:x}".format(*item), items)
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
            entry_point = EntryPoint(None, get_exception_entry_point_key(self.context), self.request)
        elif hasattr(self.context, 'entry_point'):
            logger.debug("%s", self.context)
            entry_point = self.context.entry_point

        if entry_point is None:
            assert entry_point is not None, "Entry point for view should not be None (context=%r)" % self.context
        key = entry_point.key
        assert key, "Entry point key for view should be truthy"

        # todo it might be super helpful to sanity check this value, because this generates errors
        # later that t+race to here
        self._response_dict['entry_point_key'] = entry_point.key
        self._response_dict['entry_point_template'] = 'build/templates/entry_point/%s.jinja2' % key

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


class ResourceManagerSchema(Schema):
    mapper_key = fields.String()
    title = fields.String()
    entity_type = TypeField()
    node_name = fields.String()
    pass


class ResourceSchema(Schema):
    type = TypeField(attribute='__class__')
    manager = fields.Nested(ResourceManagerSchema)
    name = fields.String(attribute='__name__')  # function=lambda x: x.__name__)
    parent = fields.Nested('self', attribute='__parent__', only=[])  # functiona=lambda x: x.__parent__)
    data = fields.Dict(attribute='_data',
                       keys=fields.String(), values=fields.Nested('ResourceSchema'))
    url = fields.Url(function=lambda x: x.url())
