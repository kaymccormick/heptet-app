import res


def test_resource(root_resource):
    name = "test"
    resource = res.Resource(name, root_resource)
    assert resource.__name__ is name
    assert resource.__parent__ is root_resource
    assert not resource.is_container

