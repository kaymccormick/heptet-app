import logging
from collections import UserDict

from requests import Request

from email_mgmt_app.resource import ResourceRegistration, ContainerResource, ResourceManager, RootResource
from pyramid.security import Allow, Authenticated


class RootFactory(UserDict):
    """

    """
    __acl__ = [(Allow, Authenticated, None),
               (Allow, Authenticated, 'view')]
    __name__ = ''
    __parent__ = None

    resources = None

    def __init__(self, request: Request) -> None:
        """

        :param request:
        """
        if not 'resources' in request.registry:
            logging.warning("registry does not have resources")
        super().__init__()
        self.data = RootFactory.resources


    def __repr__(self):
        return "RootFactory(%s)" % repr(dict(self))

    @staticmethod
    def register_model_type():
        pass

    @staticmethod
    def populate_resources(config):
        logging.warning("%s", config.registry)
        if not 'resources' in config.registry or not config.registry.resources:
            config.registry.resources = RootResource({})

        RootFactory.resources = config.registry.resources
