from unittest.mock import MagicMock

import pytest
from jinja2 import FileSystemLoader, select_autoescape, Environment

from entity import EntityFormView, EntityFormViewEntryPointGenerator


@pytest.fixture
def entity_form_view(
        config_fixture,
        app_context,
        app_request,
        entry_point_mock,
        entity_form_view_entry_point_generator,
        jinja2_env_mock,
        root_namespace_store,
        my_gen_context
):
    app_context.entry_point = entry_point_mock
    return EntityFormView(app_context, app_request)


# what mock is used here ??
def test_entity_form_view(app_request, app_context, entity_form_view, webapp_settings, jinja2_env, entry_point_mock):
    app_context.template_env = jinja2_env
    view = entity_form_view()
    assert view
