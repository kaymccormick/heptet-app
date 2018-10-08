import sys

import pytest

from heptet_app.entity import EntityFormView
from heptet_app.util import _dump
from heptet_app.myapp_config import on_context_found
from pyramid.events import ContextFound
from tests import dump_mock_calls


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
@pytest.mark.integration
def test_entity_form_view(app_request, app_context, entity_form_view, webapp_settings, jinja2_env, entry_point_mock):
    # code smell - would come from "context found."
    # we miss everything that comes from context found ...

    #app_context.template_env = jinja2_env
    # function to set these thingers?
    app_request.context = app_context
    on_context_found(ContextFound(app_request))

    view = entity_form_view()
    dump_mock_calls(entry_point_mock, entry_point_mock.mock_calls)
    #_dump(entry_point_mock.mock_calls, cb=lambda fmt, *args: print(fmt % args, file=sys.stderr), line_prefix='calls: ')
    # entry_point_mock.assert_has_calls([
    #     call.init_generator()
    # ])
    assert view
