from typing import Dict, AnyStr

from email_mgmt_app.resource import Resource, EntityResource, ResourceRegistration, ContainerResource
from pyramid.security import Allow, Authenticated



class RootFactory(ContainerResource):
    def __getitem__(self, k: AnyStr) -> Resource:
        return super().__getitem__(k)

    root_resources = {}
    __acl__ = [(Allow, Authenticated, None),
               (Allow, Authenticated, 'view')]

    def __init__(self, request) -> None:
        super().__init__(RootFactory.root_resources)

    def __repr__(self):
        return "RootFactory(%s)" % repr(dict(self))

    @staticmethod
    def register_model_type():
        pass

    @staticmethod
    def populate_resources(config):
        if config.registry['resources'] is not None:
            for (k, v) in config.registry['resources'].items():
                RootFactory.root_resources[k] = v


def register_resource(config, reg: ResourceRegistration):
    """
    register_resource is an add-on method to register resources with the Root Factory

    :param config:
    :param name:
    :param resource:
    :return:
    """
    def register():
        name = reg.name
        resource = reg.callable
        node_name = reg.node_name
        if 'resources' not in config.registry.keys():
            config.registry['resources'] = {}

        config.registry['resources'][node_name] = reg

    config.action(None, register)