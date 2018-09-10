import logging
import logging
import sys
from collections import UserDict
from threading import Lock

from pyramid.request import Request
from pyramid.security import Allow, Authenticated

from interfaces import IResource
from res import RootResource

logger = logging.getLogger(__name__)

lock = Lock()



def get_root(request: Request):
    lock.acquire()
    if hasattr(sys.modules[__name__], "_root"):
        root = getattr(sys.modules[__name__], "_root")
        lock.release()
        return root

    root = RootResource()
    setattr(sys.modules[__name__], "_root", root)
    lock.release()
    return root


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
        return get_root(request)
        logger.debug("Initializing: %s", repr(request))
        root = request.registry.queryUtility(IResource, 'root_resource')
        # data = root.get_data()
        # logger.debug("data is %s", data)
        # root2 = root.get_root_resource()
        # logger.debug("root = %s; root2 = %s", root, root2)
        return root

    @staticmethod
    def register_model_type():
        pass

    # @staticmethod
    # def populate_resources(config):
    #     assert config.registry.email_mgmt_app.resources is not None
    #     RootFactory.resources = config.registry.email_mgmt_app.resources
