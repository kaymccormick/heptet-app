import logging

from email_mgmt_app.entity import EntityFormViewEntryPointGenerator

logger = logging.getLogger(__name__)

MY_JS_VARS = ('js_imports', 'js_stmts', 'ready_stmts')


def test_generate(make_generator_context, mapper_info_mock, entry_point_mock):
    gctx = make_generator_context(entry_point_mock)
    x = EntityFormViewEntryPointGenerator(gctx)
    x.generate()
    logger.critical("%r", gctx.template_vars)
    assert set(gctx.template_vars.keys()) == set(MY_JS_VARS)
    logger.critical("%r", gctx)


    assert 0


def test_form_representation(entity_form_view_entry_point_generator):
    r = entity_form_view_entry_point_generator.form_representation()
