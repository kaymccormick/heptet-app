import logging

import pytest

from email_mgmt_app.process import GenerateEntryPointProcess, ProcessContext

logger = logging.getLogger(__name__)


@pytest.fixture
def make_generate_entry_point_process():
    def _make_generate_entry_point_process(process_context, entry_point):
        return GenerateEntryPointProcess(process_context, entry_point)

    return _make_generate_entry_point_process


@pytest.fixture
def generate_entry_point_process(process_context, entry_point_mock):
    return GenerateEntryPointProcess(process_context, entry_point_mock)


@pytest.fixture
def process_context(jinja2_env, asset_manager_mock):
    return ProcessContext({}, jinja2_env, asset_manager_mock)


@pytest.fixture
def make_process_context():
    def _make_process_context(settings, template_env, asset_manager):
        return ProcessContext(settings, template_env, asset_manager)

    return _make_process_context


def test_generate_entry_point_process_process(
        make_process_context,
        jinja2_env,
        asset_manager_mock_wraps_virtual,
        make_generate_entry_point_process,
        make_entry_point
):
    process_context = make_process_context({}, jinja2_env, asset_manager_mock_wraps_virtual)
    entry_point = make_entry_point('test1')
    generate_entry_point_process = make_generate_entry_point_process(process_context, entry_point)
    generate_entry_point_process.process()
    for k, v in process_context.asset_manager.assets.items():
        assert v.content.lower().find('jquery') != -1
