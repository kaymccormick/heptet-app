from unittest import TestCase
from unittest.mock import MagicMock

from pyramid_tm.tests import DummyRequest

from email_mgmt_app.entity import EntityFormViewEntryPointGenerator


class TestEntityFormViewEntryPointGenerator(TestCase):

    def setUp(self):
        super().setUp()
        ep = MagicMock()
        request = DummyRequest()
        self.epg = EntityFormViewEntryPointGenerator(ep, request)

    def test_form_representation(self):
        pass
