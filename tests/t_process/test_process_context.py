from unittest.mock import MagicMock
from heptet_app.process import ProcessContext
import pytest

@pytest.fixture
def process_context_1(jinja2_env_mock,
                   asset_manager_mock_wraps_virtual,
                   root_namespace_store):
    return ProcessContext({},
                   jinja2_env_mock,
                   asset_manager_mock_wraps_virtual,
                   root_namespace_store)

def test_pctx_init(process_context_1, jinja2_env_mock,
                   asset_manager_mock_wraps_virtual,
                   root_namespace_store):
    pc = process_context_1
    assert jinja2_env_mock is pc.template_env
    assert asset_manager_mock_wraps_virtual is pc.asset_manager


