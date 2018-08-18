from collections import UserDict, OrderedDict
from typing import AnyStr, Callable, Dict, NewType

import pyramid
from pyramid.config import Configurator

class ResourceOperation():
    def __init__(self, name, view, renderer=None) -> None:
        self._renderer = renderer
        self._view = view
        self._name = name


class ResourceManager():
    def __init__(self, config: Configurator, entity_type) -> None:
        self._entity_type = entity_type
        self._config = config
        self._ops = []

    def operation(self, name, view, renderer=None) -> None:
        op = ResourceOperation(name, view, renderer=renderer)
        self._ops.append(op)


class ResourceRegistration():
    def __str__(self):
        def class_str(class_):
            if class_:
                return class_.__module__ + '.' + class_.__name__
            return str(None)

        return "RR {\n  name\t\t\t= %s;\n  node_name\t\t= %s;\n  view\t\t\t= %s;\n  entity_type\t= %s;\n}" % (self.name, self.node_name, class_str(self.view), class_str(self.entity_type))

    def __init__(self, name: AnyStr, title: AnyStr=None, view=None, callable: Callable=None, node_name: AnyStr=None, entity_type=None,
                 factory_method: Callable=None) -> None:
        super().__init__()
        self._title = title
        self._factory_method = factory_method
        self._view = view

        if self._factory_method is None:

            def factory(reg: ResourceRegistration, mgr: ResourceManager):
                return ContainerResource({}, reg=reg, mgr=mgr)

            self._factory_method = factory

        self._name = name
        self._callable = callable
        if node_name is None:
            node_name = name
        self._node_name = node_name
        self._entity_type = entity_type
        self._view = view

    @property
    def callable(self):
        return self._callable

    @property
    def name(self):
        return self._name

    @property
    def node_name(self):
        return self._node_name

    @property
    def factory_method(self) -> Callable:
        return self._factory_method

    @property
    def view(self):
        return self._view

    @property
    def entity_type(self):
        return self._entity_type

    @property
    def title(self):
        return self._title or self._name


class Resource:
    def __init__(self, reg: ResourceRegistration, mgr: ResourceManager, title: AnyStr=None) -> None:
        self._title = title
        if not title and reg:
            self._title = reg.title
        self._registration = reg
        assert reg
        self.__name__ = reg.node_name
        self._entity_type = reg.entity_type
        self._resource_manager = mgr


    def __str__(self):
        return "Resource[%s,\n%s]" % (self.registration.view, self.registration.entity_type)

    def __repr__(self):
        return str(self)

    @property
    def title(self):
        return self._title

    def path(self):
        return pyramid.threadlocal.get_current_request().resource_path(self)

    def url(self):
        return pyramid.threadlocal.get_current_request().resource_url(self)

    @property
    def registration(self):
        return self._registration

    @property
    def entity_type(self):
        return self._entity_type

    @property
    def resource_manager(self):
        return self._resource_manager


class ContainerResource(Resource, UserDict):
    def __init__(self, dict_init, reg: ResourceRegistration, mgr: ResourceManager) -> None:
        super().__init__(reg, mgr)
        self.data = OrderedDict(dict_init)

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

class NodeNamePredicate():

    def __init__(self, val, config) -> None:
        self._val = val
        self._config = config

    def text(self):
        return 'node_name = %s' % (self._val)

    phash = text

    def __call__(self, context, request):
        if isinstance(context, ResourceRegistration) and context.node_name == self._val:
            return True
        return False


