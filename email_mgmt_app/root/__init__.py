import logging
from typing import Dict, AnyStr

from email_mgmt_app.resource import Resource, EntityResource, ResourceRegistration, ContainerResource
from pyramid.security import Allow, Authenticated


class RootFactory(ContainerResource):
    __name__ = ''
    __parent__ = None

    def __getitem__(self, k: AnyStr) -> Resource:
        return super().__getitem__(k)

    root_resources = {}
    __acl__ = [(Allow, Authenticated, None),
               (Allow, Authenticated, 'view')]

    def __init__(self, request) -> None:
        logging.debug("initializing Root Factory with %s", str(RootFactory.root_resources))
        super().__init__(RootFactory.root_resources, reg=ResourceRegistration('root', 'Home', node_name=''))

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
                logging.debug("RootFactory.root_resources[%s] = %s [%s]", repr(k), repr(v), type(v))



def register_resource(config, reg: ResourceRegistration):
    """
    register_resource is an add-on method to register resources with the Root Factory

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
            config.registry['resources'] = {}

        o = reg.factory_method(reg)
        config.registry['resources'][node_name] = o
        logging.debug("o = %s", o)

    config.action(None, register)