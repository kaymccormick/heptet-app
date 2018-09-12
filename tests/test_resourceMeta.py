import logging

from email_mgmt_app import get_root, RootResource, Resource

logger = logging.getLogger(__name__)

def test_resource_meta(root_resource, entry_point):
    root = root_resource
    a = root.sub_resource('a', entry_point)
    b = root.sub_resource('b', entry_point)
    assert root['a'] is a
    assert root['b'] is b
    logger.warning("%s, %s", type(a), type(b))


def test_root_Resource(app_request):
    root = get_root(app_request)
    root2 = get_root(app_request)
    assert root is root2
    #assert type(root) == RootResource
