import logging

import pytest
import sys
from heptet_app import get_root, ResourceManager

logger = logging.getLogger(__name__)


@pytest.mark.integration
def test_rm_add_action(config_fixture, resource_manager, app_request):
    logger.warning("%s", resource_manager)

    # config_fixture.action(None, resource_manager.add_action)
    root = get_root(app_request)
    for k, v in root.items():
        print("k, v is %s = %s" % (k, v), file=sys.stderr)
    # logger.warning("%s", root.items())
    assert 0


def test_resource_manager_init_1():
    mapper_key = "random"
    title = "random"
    node_name = "random"
    out = ResourceManager(mapper_key, title, int, node_name)
    assert mapper_key == out.mapper_key
    assert title == out.title
    assert node_name == out.node_name
