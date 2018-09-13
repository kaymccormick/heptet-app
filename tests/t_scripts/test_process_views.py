import pytest

import process
import process_views


@pytest.mark.integration
def test_process_views_main():
    process_views.main(["-c", r"development.ini"])


def test_process_views(app_registry_mock, asset_manager_mock, process_context_mock, entry_point_mock, jinja2_env_mock,
                       app_request):
    ep_iterable = [(entry_point_mock.key, entry_point_mock)]
    process.process_views(app_registry_mock, jinja2_env_mock, asset_manager_mock, process_context_mock, ep_iterable,
                          app_request)
