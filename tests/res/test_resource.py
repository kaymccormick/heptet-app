from email_mgmt_app import Resource
import logging

logger = logging.getLogger(__name__)


def test_resource(root_resource, resource_manager):
    name = "test"
    resource = Resource(resource_manager, name, root_resource)
    logger.critical("root = %r", root_resource)
    assert resource.__name__ is name
    assert resource.__parent__ is root_resource
    logger.critical("resource = %r", resource)
    r2 = resource.sub_resource('test2', )
    logger.critical("r2 = %r", r2)

    assert not resource.is_container
    assert 0

