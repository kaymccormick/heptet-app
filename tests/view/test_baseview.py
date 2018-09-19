import logging

import pytest

logger = logging.getLogger(__name__)


@pytest.mark.integration
def test_(view_baseview):
    result = view_baseview()
    logger.critical("%r", result)
