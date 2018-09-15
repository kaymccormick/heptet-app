import sys

import pytest

from entity import EntityFormView
from util import _dump


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

    x = EntityFormView(app_context, app_request)
    return x


# what mock is used here ??
def test_entity_form_view(app_request, app_context, entity_form_view, webapp_settings, jinja2_env, entry_point_mock):
    # code smell - would come from "context found."
    app_context.template_env = jinja2_env

    view = entity_form_view()
    _dump(entry_point_mock.mock_calls, cb=lambda fmt, *args: print(fmt % args, file=sys.stderr), line_prefix='calls: ')
    # entry_point_mock.assert_has_calls([
    #     call.init_generator()
    # ])
    assert view
