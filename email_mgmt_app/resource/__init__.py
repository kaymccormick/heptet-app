import logging
from collections import UserDict, OrderedDict
from collections.__init__ import OrderedDict
from typing import AnyStr, Callable, Dict, NewType

import pyramid
from pyramid.config import Configurator


class ResourceOperation:
    """
    Class encapsulating an operation on a resource
    """
    def __init__(self, name, view, renderer=None) -> None:
        """

        :param name: name of the operation - add, view, etc
        :param view: associated view
        :param renderer: associated renderer
        """
        self._renderer = renderer
        self._view = view
        self._name = name


class ResourceManager:
    """
    ResourceManager class. Provides access to resource operations.
    """
    def __init__(self, config: Configurator, entity_type) -> None:
        """
        Instantiate a new instance of ResourceManager
        :param config: Configurator class
        :param entity_type: Associated entity type
        """
        self._entity_type = entity_type
        self._config = config
        self._ops = []

    def operation(self, name, view, renderer=None) -> None:
        """
        Add operation to resource manager.
        :param name:
        :param view:
        :param renderer:
        :return:
        """
        op = ResourceOperation(name, view, renderer=renderer)
        self._ops.append(op)


class ResourceRegistration:
    """
    ResourceRegistration
    """
    def __str__(self):
        def class_str(class_):
            if class_:
                return class_.__module__ + '.' + class_.__name__
            return str(None)

        return "RR {\n  name\t\t\t= %s;\n  node_name\t\t= %s;\n  view\t\t\t= %s;\n  entity_type\t= %s;\n}" % (self.name, self.node_name, class_str(self.view), class_str(self.entity_type))

    def __init__(self, name: AnyStr, title: AnyStr=None, view=None, callable: Callable=None, node_name: AnyStr=None, entity_type=None,
                 factory_method: Callable=None) -> None:
        """
        :param name:
        Instantiate a ResourceRegistration
        :param title:
        :param view:
        :param callable:
        :param node_name:
        :param entity_type:
        :param factory_method:
        """
        super().__init__()
        self._title = title
        self._factory_method = factory_method
        self._view = view

        if self._factory_method is None:


            def factory(*args, **kwargs):
                return ContainerResource({}, *args, **kwargs)

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
        """
        Property callable
        :return:
        """
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
    def __init__(self, reg: ResourceRegistration=None, mgr: ResourceManager=None, name: AnyStr=None, parent: 'ContainerResource'=None, title: AnyStr=None) -> None:
        self._title = title
        if not title and reg:
            self._title = reg.title
        self._registration = reg
        self.__name__ = name
        self.___parent__ = parent
        if reg:
            self._entity_type = reg.entity_type
        self._resource_manager = mgr

    def attach(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name


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
    def __init__(self, dict_init, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.data = OrderedDict(dict_init)


class LeafResource(Resource):
    def __getattr__(self, item):
        raise KeyError


class RootResource(ContainerResource):

    def __init__(self, dict_init, *args, **kwargs) -> None:
        logging.warning("%s %s", args, kwargs)
        self.__name__ = ''
        self.__parent__ = None
        super().__init__(dict_init, *args, **kwargs)


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


def register_resource(config: Configurator,
                      reg: ResourceRegistration,
                      mgr: ResourceManager):
    """
    register_resource is an add-on method to register resources with the Root Factory

    notes: right now there is really no case for a multi-level hierarchy -
    everything is a child of the root

    :param mgr:
    :param reg:
    :param config:
    :return:
    """
    def register():
        logging.debug("registering %s", reg)
        name = reg.name
        # this we dont seem to be using
        resource = reg.callable
        node_name = reg.node_name
        root = None
        if 'resources' not in config.registry.keys():
            root = RootResource({})
            config.registry.resources = root
        else:
            root = config.registry.resources

        #this should be moved out of config!

        root[node_name] = reg.factory_method(reg, mgr,
                                             name=node_name,
                                             parent=config.registry.resources)

    config.action(None, register)