import logging
from collections import OrderedDict, UserDict

from typing import Dict, AnyStr

from email_mgmt_app.resource import Resource, EntityResource, ResourceRegistration, ContainerResource, ResourceManager
from pyramid.security import Allow, Authenticated


class RootFactory(ContainerResource):
    """

    """
    __acl__ = [(Allow, Authenticated, None),
               (Allow, Authenticated, 'view')]
    __name__ = ''
    __parent__ = None

    class RootResources(ContainerResource):
        """

        """

        @classmethod
        def static_init(cls, param):
            logging.debug("my cls = %s (param = %s)", repr(cls), repr(param))
            return cls(param)

    root_resources = RootResources.static_init({})

    def __init__(self, request) -> None:
        """

        :param request:
        """
        logging.debug("initializing Root Factory with %s", str(RootFactory.root_resources))
        super().__init__(RootFactory.root_resources,
                         ResourceRegistration('root', 'Home', node_name = ''),
                         ResourceManager(None, None),
                         )


    def __repr__(self):
        return "RootFactory(%s)" % repr(dict(self))

    @staticmethod
    def register_model_type():
        pass

    @staticmethod
    def populate_resources(config):
        logging.debug("populating resources from config")
        if config.registry['resources'] is not None:
            for (k, v) in config.registry['resources'].items():
                RootFactory.root_resources[k] = v
                v.__name__ = k
                logging.debug("RootFactory.root_resources[%s] = %s [%s]", repr(k), repr(v), type(v))


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
        resource = reg.callable
        node_name = reg.node_name
        if 'resources' not in config.registry.keys():
            config.registry['resources'] = OrderedDict()

        o = reg.factory_method(reg, mgr)
        config.registry['resources'][node_name] = o
        logging.debug("o = %s", o)

    config.action(None, register)