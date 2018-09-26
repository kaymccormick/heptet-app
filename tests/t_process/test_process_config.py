import logging
from unittest.mock import MagicMock, call

import pytest
from pyramid.config import Configurator

import email_mgmt_app.myapp_config
from email_mgmt_app.process import config_process_struct
from tests import dump_mock_calls, mock_wrap_config

logger = logging.getLogger(__name__)


@pytest.mark.integration
def test_process_config_include(config_mock_wrap):
    config = config_mock_wrap
    config.include(email_mgmt_app.process.includeme)
    assert 0


@pytest.mark.integration
def test_process_config_include(app_registry_mock):
    config = MagicMock(Configurator)
    mock = mock_wrap_config(None, app_registry_mock)
    email_mgmt_app.process.includeme(mock)
    mock.assert_has_calls([call.include('.viewderiver'), call.include('.entity')])
    dump_mock_calls(mock, mock.mock_calls)
    assert 0
