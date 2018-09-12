from unittest.mock import MagicMock

import pytest
from jinja2 import FileSystemLoader, select_autoescape, Environment

from entity import EntityFormView, EntityFormViewEntryPointGenerator


@pytest.fixture
def entity_form_view(
        config_fixture,
        app_context,
        app_request,
        entry_point,
        entity_form_view_entry_point_generator,
        jinja2_env_mock,
        root_namespace_store,
        my_gen_context
):
    app_context.entry_point = entry_point
    app_context.entry_point.init_generator = lambda x,y,z: setattr(entry_point, "generator", EntityFormViewEntryPointGenerator(my_gen_context))
    #app_context.entry_point.key.side_effect = "key"
    #EntityFormView.entry_point = entry_point
    #EntityFormView.template_env = jinja2_env
    #EntityFormView.root_namespace = root_namespace_store    entry_point.generator = entity_form_view_entry_point_generator
    return EntityFormView(app_context, app_request)


def test_entity_form_view(app_request, app_context, entity_form_view, webapp_settings):
    jinja2_loader_template_path = webapp_settings['email_mgmt_app.jinja2_loader_template_path'].split(':')
    env = Environment(loader=FileSystemLoader(jinja2_loader_template_path),
                      autoescape=select_autoescape(default=False))

    #app_context.entry_point = MagicMock(EntryPoint)
    app_request.template_env = lambda: env;
    view = entity_form_view()
    assert view
