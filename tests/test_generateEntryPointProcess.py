import logging
import sys
from unittest.mock import mock_open, patch, Mock

import pytest

from email_mgmt_app.process import GenerateEntryPointProcess, ProcessContext

logger = logging.getLogger(__name__)


@pytest.fixture
def generate_entry_point_process(process_context, entry_point_mock):
    return GenerateEntryPointProcess(process_context, entry_point_mock)


@pytest.fixture
def process_context(jinja2_env_mock, asset_manager_mock):
    return ProcessContext({}, jinja2_env_mock, asset_manager_mock)


def test_generate_entry_point_process_process(generate_entry_point_process, process_context):
    generate_entry_point_process.process()


