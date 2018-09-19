import sys

import pytest

from email_mgmt_app.entity import EntityFormView
from email_mgmt_app.util import _dump


@pytest.fixture
def entity_form_view(
        config_fixture,
        app_context,
        app_request,
        entry_point_mock,
        jinja2_env_mock,
        root_namespace_store,

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
