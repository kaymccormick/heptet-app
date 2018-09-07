from unittest import TestCase
from unittest.mock import MagicMock

import pytest
from pyramid_tm.tests import DummyRequest
from zope.component import adapter
from zope.interface import implementer

from email_mgmt_app.entity import EntityFormViewEntryPointGenerator, ITemplateVariable
from interfaces import ITemplateSource, ITemplate, ICollector
from pyramid_jinja2 import IJinja2Environment


@pytest.fixture
def entity_form_view_entry_point_generator(form_context, form_representation_builder, entry_point, entity_form_view,
                                           app_request):
    return EntityFormViewEntryPointGenerator(form_context, form_representation_builder, entry_point, entity_form_view,
                                             app_request)


def test_generate(entity_form_view_entry_point_generator):
    entity_form_view_entry_point_generator.generate()
    entry_point = entity_form_view_entry_point_generator.entry_point
    assert entry_point.vars
    assert entity_form_view_entry_point_generator


class TestEntityFormViewEntryPointGenerator(TestCase):
    pass
