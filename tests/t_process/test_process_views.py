import logging

from email_mgmt_app.process import process_views, process_view
from tests.common import MakeEntryPoint

logger = logging.getLogger()

def test_process_views_new(app_registry_mock, process_context, entry_point_mock):
    ep_iterable = [(entry_point_mock.key, entry_point_mock)]
    process_views(app_registry_mock, process_context, ep_iterable)
    logger.critical("%r", process_context.asset_manager.mock_calls)
    assert 0


def test_process_views(app_registry_mock, asset_manager_mock, process_context_mock, entry_point_mock, jinja2_env_mock,
                       app_request, make_entry_point: MakeEntryPoint):
    # for name in 'abcdef':
    #     make_entry_point(
    ep_iterable = [(entry_point_mock.key, entry_point_mock)]
    process_views(app_registry_mock, jinja2_env_mock, process_context_mock, ep_iterable)
    logger.critical("%r", process_context_mock.mock_calls)
    logger.critical("%r", asset_manager_mock.mock_calls)


def test_process_view(entry_point_mock, process_context_mock, app_registry_mock,
                      entry_point_generator_mock):
    process_view(app_registry_mock, process_context_mock, entry_point_mock)

