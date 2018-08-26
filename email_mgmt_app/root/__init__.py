import logging
from collections import UserDict

from pyramid.request import Request

from email_mgmt_app.res import RootResource
from pyramid.security import Allow, Authenticated


class RootFactory(UserDict):
    """
    Root Factory class supplied to pyramid.config.Configurator
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
        if not 'email_mgmt_app_resources' in request.registry:
            logging.warning("registry does not have resources")
        super().__init__()
        self.data = RootFactory.resources
        self.entity_type = None

    def __repr__(self):
        return "RootFactory(%s)" % repr(dict(self))

    @staticmethod
    def register_model_type():
        pass

    @staticmethod
    def populate_resources(config):
        logging.warning("%s", config.registry)
        if not 'email_mgmt_app_resources' in config.registry or not config.registry.email_mgmt_app_resources:
            logging.warning("OMG email_mgmt_app_resources not in config.registry")
            config.registry.email_mgmt_app_resources = RootResource({})

        RootFactory.resources = config.registry.email_mgmt_app_resources
