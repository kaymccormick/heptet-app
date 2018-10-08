import logging
import unittest
from unittest.mock import MagicMock, call

import pytest
from heptet_app.entity import EntityFormViewEntryPointGenerator

logger = logging.getLogger(__name__)


@pytest.fixture
def entity_form_view_entry_point_generator(generator_context_mock):
    return EntityFormViewEntryPointGenerator(generator_context_mock)


MY_JS_VARS = ('js_imports', 'js_stmts', 'ready_stmts')


def test_generate(
        mapper_info_mock,
        entry_point_mock,
        generator_context_mock,
        template_vars_wrapped
):
    """
    Test the "generate" method of EntryPointGenerator - right now, focuses on the hard-coded EntityFormViewEntryPointGenerator class.
    Using a mock generator context does not really allow us to check the template variables as we are attempting to do.
    :param make_generator_context:
    :param mapper_info_mock:
    :param entry_point_mock:
    :param generator_context_mock:
    :return:
    """
    gctx = generator_context_mock
    x = EntityFormViewEntryPointGenerator(generator_context_mock)
    x.generate()
    logger.critical("%r", gctx.mock_calls)
    logger.critical("%r", gctx.template_vars.mock_calls)
    logger.critical("te = %r", gctx.template_env.mock_calls)
    assert set(MY_JS_VARS) == set(template_vars_wrapped.keys())

    logger.critical("%r", gctx)


def test_generate_2(make_generator_context,
                    mapper_info_mock,
                    entry_point_mock,
                    generator_context_mock):
    gctx = generator_context_mock
    new = MagicMock()
    with unittest.mock.patch('heptet_app.entity.EntityFormViewEntryPointGenerator.form_representation', new):
        x = EntityFormViewEntryPointGenerator(generator_context_mock)

        x.generate()

    logger.critical("%r", gctx.mock_calls)
    logger.critical("%r", new.mock_calls)
    logger.critical("%r", gctx.template_vars)
    keys = gctx.template_vars.keys()
    assert set(keys) == set(MY_JS_VARS)
    logger.critical("%r", gctx)


def test_form_representation(entity_form_view_entry_point_generator):
    r = entity_form_view_entry_point_generator.form_representation()
