from email_mgmt_app import RootResource
import logging

logger = logging.getLogger(__name__)

def test_rm_add_action(config_fixture, resource_manager):
    logger.warning("%s", resource_manager)
    config_fixture.add_resource_manager(resource_manager)
    #config_fixture.action(None, resource_manager.add_action)
    config_fixture.commit()
    root = RootResource()
    assert len(root.items()) == 1





