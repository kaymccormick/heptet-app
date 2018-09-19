import logging
import unittest
from unittest.mock import MagicMock

import pytest
from email_mgmt_app.entity import EntityFormViewEntryPointGenerator

logger = logging.getLogger(__name__)


@pytest.fixture
def entity_form_view_entry_point_generator(generator_context_mock):
    return EntityFormViewEntryPointGenerator(generator_context_mock)


MY_JS_VARS = ('js_imports', 'js_stmts', 'ready_stmts')


def test_generate(make_generator_context, mapper_info_mock, entry_point_mock, generator_context_mock):
    gctx = generator_context_mock
    x = EntityFormViewEntryPointGenerator(generator_context_mock)
    x.generate()
    logger.critical("%r", gctx.mock_calls)
    logger.critical("%r", gctx.template_vars)
    assert set(MY_JS_VARS) == set(gctx.template_vars.keys())
    logger.critical("%r", gctx)


def test_generate_2(make_generator_context,
                    mapper_info_mock,
                    entry_point_mock,
                    generator_context_mock):
    gctx = generator_context_mock
    new = MagicMock()
    with unittest.mock.patch('email_mgmt_app.entity.EntityFormViewEntryPointGenerator.form_representation', new):
        x = EntityFormViewEntryPointGenerator(generator_context_mock)

        x.generate()

    logger.critical("%r", gctx.mock_calls)
    logger.critical("%r", new.mock_calls)
    logger.critical("%r", gctx.template_vars)
    assert set(gctx.template_vars.keys()) == set(MY_JS_VARS)
    logger.critical("%r", gctx)


def test_form_representation(entity_form_view_entry_point_generator):
    r = entity_form_view_entry_point_generator.form_representation()
