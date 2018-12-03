import logging

import pytest
from heptet_app.mschema import AssetManagerSchema

from heptet_app.process import process_views, process_view

logger = logging.getLogger()


def test_(asset_manager_mock_wraps_virtual, make_entry_point):
    ep = make_entry_point('test1')
    v = asset_manager_mock_wraps_virtual.create_asset(ep)
    with v.open('w') as f:
        f.write('test 123')

    print(v)

@pytest.mark.integration
def test_process_views_new(app_registry_mock, process_context, entry_point_mock):
    ep_iterable = [(entry_point_mock.key, entry_point_mock)]
    config = {}
    process_views(app_registry_mock, config, process_context, ep_iterable)
    logger.critical("%r", process_context.asset_manager.mock_calls)
    schema = AssetManagerSchema()
    logger.critical("x = %r", schema.dump(process_context.asset_manager))


def test_process_views(app_registry_mock, asset_manager_mock, process_context_mock, entry_point_mock, jinja2_env_mock,
                       app_request, make_entry_point):
    # for name in 'abcdef':
    #     make_entry_point(
    ep_iterable = [(entry_point_mock.key, entry_point_mock)]
    process_views(app_registry_mock, jinja2_env_mock, process_context_mock, ep_iterable)
    logger.critical("%r", process_context_mock.mock_calls)
    logger.critical("%r", asset_manager_mock.mock_calls)


def test_process_view(entry_point_mock, process_context_mock, app_registry_mock,
                      entry_point_generator_mock):
    config = {}
    process_view(app_registry_mock, config, process_context_mock, entry_point_mock)
