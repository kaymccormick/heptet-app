import re
import logging

import pytest
from heptet_app.mschema import AssetManagerSchema
from unittest.mock import call
from heptet_app.process import process_views, process_view

logger = logging.getLogger()


def test_virtual(asset_manager_mock_wraps_virtual, make_entry_point,
                 virtual_asset_manager):
    ep = make_entry_point('test1')
    am = asset_manager_mock_wraps_virtual
    vam = virtual_asset_manager
    v = am.create_asset(ep)
    with v.open('w') as f:
        f.write('test 123')

    foundEp = False
    for k, v in am.assets.items():
        if k is ep:
            assert not foundEp
            foundEp = True
            assert "test 123" == v.content

    assert foundEp

@pytest.mark.integration
def test_process_views_mocked(app_registry_mock, process_context, entry_point_mock):
    ep_iterable = [(entry_point_mock.key, entry_point_mock)]
    config = {}
    process_views(app_registry_mock, config, process_context, ep_iterable)
    logger.critical("%r", process_context.asset_manager.mock_calls)
    logger.critical("%r", app_registry_mock.mock_calls)
    logger.critical("x = %r", process_context.asset_manager)

# tbis is partially mocked- 
def test_process_views(app_registry_mock, asset_manager_mock,
                       process_context_mock, entry_point_mock,
                       jinja2_env_mock,
                       app_request, make_entry_point):
    # for name in 'abcdef':
    #     make_entry_point(
    ep_iterable = [(entry_point_mock.key, entry_point_mock)]
    process_views(app_registry_mock, jinja2_env_mock, process_context_mock, ep_iterable)
    logger.critical("%r", process_context_mock.mock_calls)
    logger.critical("%r", asset_manager_mock.mock_calls)
    assert 0


def test_process_view(entry_point_mock, process_context_mock, app_registry_mock,
                      entry_point_generator_mock):
    config = {}
    process_view(app_registry_mock, config, process_context_mock, entry_point_mock)


def test_process_views_2(config_fixture, process_context, entry_point_mock, caplog):
    with caplog.at_level(logging.DEBUG):
        config = {}
        ep = [(entry_point_mock.key, entry_point_mock)]
        process_views(config_fixture.registry, {}, process_context, ep)

        for k, v in process_context.asset_manager.assets.items():
            content = v.content
            # check for jquery and bootstrap, obviously fragile
            assert re.search(r'\Wimport\s+jQuery\s+from\s+"jquery"\s*;', content)
            assert re.search(r'\Wimport\s+\'bootstrap.*\.css\';', content)
            logger.debug("%r = %r", k, v)


        assert 0


