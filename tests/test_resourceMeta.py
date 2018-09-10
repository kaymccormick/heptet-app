import logging

from res import Resource, RootResource
from root import get_root

logger = logging.getLogger(__name__)

def test_resource_meta():
    root = RootResource()
    a = Resource(name='a', parent=root)
    b = Resource(name='b', parent=root)
    logger.warning("%s, %s", type(a), type(b))

def test_root_Resource(app_request):
    root = get_root(app_request)
    root2 = get_root(app_request)
    assert root is root2
    #assert type(root) == RootResource
