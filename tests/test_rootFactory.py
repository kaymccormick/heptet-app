import logging
from unittest import TestCase

from email_mgmt_app import RootFactory
from pyramid.testing import DummyRequest

logger = logging.getLogger(__name__)

class TestRootFactory(TestCase):

    def setUp(self):
        super().setUp()
        request = DummyRequest()
        self.rf = RootFactory(request)
        logger.critical("in setup %s", self.rf)

    def test___init__(self):
        logger.critical("rf = %s", repr(self.rf))

