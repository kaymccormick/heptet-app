import json
import logging

import pytest
from email_mgmt_app import Resource, get_root, ResourceSchema

logger = logging.getLogger(__name__)


@pytest.mark.integration
def test_add_resources(make_resource, app_request, root_resource):
    root1 = root_resource
    res1 = make_resource('resource1')
    root1[res1.__name__] = res1
    root2 = get_root(app_request)
    res2 = make_resource('resource2')
    root2[res2.__name__] = res2
    assert res1.__name__ in root2


def test_add_resources_2(root_resource, entry_point_mock):
    # print(textwrap.fill(repr(root_resource), 120), file=sys.stderr)
    root = root_resource
    assert 0 == len(root)
    a = root.sub_resource('a', entry_point_mock)
    assert 0 == len(a)
    assert 1 == len(root)
    b = root.sub_resource('b', entry_point_mock)
    assert 0 == len(b)
    assert 2 == len(root)

    assert root['a'] is a
    assert root['b'] is b
    logger.warning("%s, %s", type(a), type(b))


def test_root_Resource(app_request):
    root = get_root(app_request)
    root2 = get_root(app_request)
    assert root is root2
    # assert type(root) == RootResource


def test_resource(root_resource, entry_point_mock):
    name = "test"
    resource = Resource(name, root_resource, entry_point_mock)
    logger.critical("root = %r", root_resource)
    assert resource.__name__ is name
    assert resource.__parent__ is root_resource
    logger.critical("resource = %r", resource)
    r2 = resource.sub_resource('test2', entry_point_mock)
    logger.critical("r2 = %r", r2)

    assert not resource.is_container


def test_resource_dump(root_resource):
    s = ResourceSchema()
    logger.critical("%s", json.dumps(s.dump(root_resource), indent=4))


def test_resource_url(root_resource, app_request):
    with pytest.raises(AssertionError):
        path = app_request.resource_path(root_resource, _host='localhost')
        assert '/' == path


def _thread(root_resource):
    num = 1000
    i = 0
    while i < num:
        resource = root_resource.sub_resource("%04d" % i, None)
        logger.critical("resource = %r", resource)
        import time
        i = i + 1



#
#
# def test_add_resource_threaded(root_resource):
#     import threading
#     num_threads = 100
#     i = 0
#     threads = []
#     while i < num_threads:
#         thread = threading.Thread(target=_thread, args=[root_resource])
#         thread.start()
#         threads.append(thread)
#
#         i = i + 1
#
#     while threads:
#         threads.pop().join()
#
#     assert 0
#
#
