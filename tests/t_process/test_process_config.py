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

@pytest.mark.integration
def test_process_config_include_2(app_registry_mock):
    config = Configurator()
    mock = mock_wrap_config(config, app_registry_mock)
    with pytest.raises(ModuleNotFoundError):
        email_mgmt_app.process.includeme(mock)
        # we should never get here
        mock.assert_has_calls([call.include('.viewderiver'), call.include('.entity')])
        dump_mock_calls(mock, mock.mock_calls)
        assert "We should have experiened an error."

def new_configurator(cls, *args, **kwargs):
    config = object.__new__(cls)
    mock = mock_wrap_config(config, None)
    return mock



@pytest.mark.integration
def test_process_config_include_3(app_registry_mock, monkeypatch):
    config = Configurator()
    mock = mock_wrap_config(config, app_registry_mock)
    with monkeypatch.context() as m:
        oldattr = getattr(Configurator, '__new__')
        m.setattr(Configurator, '__new__', new_configurator)
        with pytest.raises(ModuleNotFoundError):

            mock.include(email_mgmt_app.process.includeme)
            # we should never get here
            #mock.assert_has_calls([call.include('.viewderiver'), call.include('.entity')])
            dump_mock_calls(mock, mock.mock_calls)
            assert "We should have experiened an error."

