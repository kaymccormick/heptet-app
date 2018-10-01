import logging

import pytest
from heptet_app import _add_resmgr_action

logger = logging.getLogger(__name__)


@pytest.mark.integration
def test_add_resmgr_action(config_fixture, resource_manager_mock):
    config = config_fixture
    _add_resmgr_action(config, resource_manager_mock)
    logger.critical("%r " , resource_manager_mock.mock_calls)
