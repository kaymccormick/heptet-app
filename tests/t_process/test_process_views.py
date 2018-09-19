import logging

import pytest
from email_mgmt_app.process import process_views, process_view
from tests.common import MakeEntryPoint

logger = logging.getLogger()

@pytest.mark.integration
def test_process_views_main():
    main(["-c", r"development.ini"])


def test_process_views(app_registry_mock, asset_manager_mock, process_context_mock, entry_point_mock, jinja2_env_mock,
                       app_request, make_entry_point: MakeEntryPoint):
    # for name in 'abcdef':
    #     make_entry_point(
    ep_iterable = [(entry_point_mock.key, entry_point_mock)]
    process_views(app_registry_mock, jinja2_env_mock, process_context_mock, ep_iterable,
                  app_request)
    logger.critical("%r", process_context_mock.mock_calls)
    logger.critical("%r", asset_manager_mock.mock_calls)
    assert 0



def test_process_view(generator_context_mock, entry_point_mock, process_context_mock, app_registry_mock,
                      entry_point_generator_mock):
    process_view(generator_context_mock, entry_point_mock, process_context_mock, app_registry_mock, entry_point_generator_mock)
