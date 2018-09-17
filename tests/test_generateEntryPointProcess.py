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
def process_context(jinja2_env_mock, asset_manager):
    return ProcessContext({}, jinja2_env_mock, asset_manager)


def test_(generate_entry_point_process):
    m = mock_open()
    m2 = m()
    _x = None

    def se(x):
        print(x, file=sys.stderr)
        _x = x
        return

    with patch('process.open', m, create=True):
        generate_entry_point_process.process()
    calls_ = m2.write.mock_calls[0]
    name = None
    if len(calls_) == 3:
        (name, args, kwargs) = calls_
    elif len(calls_) == 2:
        (args, kwargs) = calls_

    m2 = m()  # type: Mock
    logger.critical("!!! %r", _x)

    for x in m2.mock_calls:
        logger.critical("!! %r", x)
