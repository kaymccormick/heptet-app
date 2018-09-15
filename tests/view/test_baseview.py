import logging

logger = logging.getLogger(__name__)


def test_(view_baseview):
    result = view_baseview()
    logger.critical("%r", result)
