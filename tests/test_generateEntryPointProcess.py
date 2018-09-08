import pytest

from email_mgmt_app.process import GenerateEntryPointProcess, ProcessContext, AssetManager


@pytest.fixture
def generate_entry_point_process(process_context, entry_point):
    return GenerateEntryPointProcess(process_context, entry_point)


@pytest.fixture
def asset_manager():
    return AssetManager("tmpdir", mkdir=True)


@pytest.fixture
def process_context(jinja2_env, asset_manager):
    return ProcessContext({}, jinja2_env, asset_manager)


def test_(generate_entry_point_process):
    generate_entry_point_process.process()
