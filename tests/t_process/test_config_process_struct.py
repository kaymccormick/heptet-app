from heptet_app.process import config_process_struct

import logging

logger = logging.getLogger(__name__)


def test_process_config_process_struct(config_mock, process_struct_basic_model):
    config_process_struct(config_mock, process_struct_basic_model)
    logger.critical("%r", config_mock.mock_calls)

