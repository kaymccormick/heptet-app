from email_mgmt_app import get_root, ContainerResource, Resource


def test_root_resource(root_resource):
    assert isinstance(root_resource, Resource)
    assert root_resource.is_container


def test_add_resources(make_resource, app_request):
    root1 = get_root(app_request)
    res1 = make_resource('resource1')
    root1[res1.__name__] = res1
    root2 = get_root(app_request)
    res2 = make_resource('resource2')
    root2[res2.__name__] = res2
    assert res1.__name__ in root2
