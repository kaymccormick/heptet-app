import logging
from collections import UserDict

from pyramid.request import Request
from pyramid.security import Allow, Authenticated
from email_mgmt_app.res import IRootResource
from interfaces import IResource

logger = logging.getLogger(__name__)


class RootFactory(UserDict):
    """
    Root Factory class supplied to pyramid.config.Configurator
    """
    __acl__ = [(Allow, Authenticated, None),
               (Allow, Authenticated, 'view')]
    __name__ = ''
    __parent__ = None

    resources = None

    def __init__(self) -> None:
        super().__init__()
        # fixme should we be populating from this??
        self.data = RootFactory.resources or {}
        self.entity_type = None

    def __call__(self, request: Request):
        logger.debug("Initializing: %s", repr(request))
        root = request.registry.queryUtility(IResource, 'root_resource')
        # data = root.get_data()
        # logger.debug("data is %s", data)
        # root2 = root.get_root_resource()
        # logger.debug("root = %s; root2 = %s", root, root2)
        return root


    @staticmethod
    def __json__(request):
        return RootFactory.resources

    @staticmethod
    def register_model_type():
        pass

    # @staticmethod
    # def populate_resources(config):
    #     assert config.registry.email_mgmt_app.resources is not None
    #     RootFactory.resources = config.registry.email_mgmt_app.resources
