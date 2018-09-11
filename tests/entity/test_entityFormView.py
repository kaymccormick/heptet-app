import pytest

from entity import EntityFormView


@pytest.fixture
def entity_form_view(
        config_fixture,
        app_context,
        app_request,
        entry_point,
        entity_form_view_entry_point_generator,
        jinja2_env,
        root_namespace_store
):
    #EntityFormView.entry_point = entry_point
    #EntityFormView.template_env = jinja2_env
    #EntityFormView.root_namespace = root_namespace_store    entry_point.generator = entity_form_view_entry_point_generator
    return EntityFormView(app_context, app_request)


def test_entity_form_view(entity_form_view):

    view = entity_form_view()
    assert view
