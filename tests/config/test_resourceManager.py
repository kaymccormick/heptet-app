import sys

from email_mgmt_app import RootResource, get_root
import logging

logger = logging.getLogger(__name__)


def test_rm_add_action(config_fixture, resource_manager, app_request):
    logger.warning("%s", resource_manager)
    config_fixture.add_resource_manager(resource_manager)
    # config_fixture.action(None, resource_manager.add_action)
    config_fixture.commit()
    root = get_root(app_request)
    for k, v in root.items():
        print("k, v is %s = %s" % (k, v), file=sys.stderr)
    #logger.warning("%s", root.items())
