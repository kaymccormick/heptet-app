from res import Resource, ContainerResource, RootResource


def test_root_resource(root_resource):
    assert isinstance(root_resource, Resource)
    assert isinstance(root_resource, ContainerResource)
    assert root_resource.is_container


def test_add_resources(make_resource):
    root1 = RootResource()
    res1 = make_resource('resource1')
    root1[res1.__name__] = res1
    root2 = RootResource()
    res2 = make_resource('resource2')
    root2[res2.__name__] = res2
    assert res1.__name__ in root2
