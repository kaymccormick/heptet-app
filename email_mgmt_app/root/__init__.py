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
        super().__init__()
        self.data = RootFactory.resources
        self.entity_type = None

    def __repr__(self):
        return "RootFactory(%s)" % repr(dict(self))

    @staticmethod
    def __json__(request):
        return RootFactory.resources

    @staticmethod
    def register_model_type():
        pass

    @staticmethod
    def populate_resources(config):
        logging.warning("%s", config.registry)
        assert config.registry.email_mgmt_app.resources is not None
        RootFactory.resources = config.registry.email_mgmt_app.resources

