import logging

from email_mgmt_app import _add_resmgr_action

logger = logging.getLogger(__name__)


def test_add_resmgr_action(config_mock, resource_manager_mock):
    _add_resmgr_action(config_mock, resource_manager_mock)
    logger.critical("%r %r", config_mock.mock_calls, resource_manager_mock.mock_calls)
