import logging

logger = logging.getLogger(__name__)


def test_templates_1():
    from heptet_app.entity import template
    logger.critical("%s", template)
