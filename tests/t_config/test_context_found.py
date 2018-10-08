import logging
from unittest.mock import MagicMock, PropertyMock

import pytest
from jinja2 import TemplateNotFound
from pyramid.events import ContextFound

from heptet_app.myapp_config import on_context_found

logger = logging.getLogger(__name__)


@pytest.fixture
def context_found_event(app_request, app_context, app_registry_mock):
    app_request.registry = app_registry_mock
    app_request.context = app_context
    event = MagicMock(wraps=ContextFound(app_request), name='context_found_event')
    # type-wide property mock, okay for request of course
    type(event).request = PropertyMock(return_value=app_request)
    return event


@pytest.mark.integration
def test_on_context_found(app_request,
                          app_registry_mock,
                          app_context,
                          jinja2_env_mock,
                          context_found_event):
    on_context_found(context_found_event)
    assert jinja2_env_mock is app_context.template_env


@pytest.fixture
def setup_context_found(context_found_event):
    return context_found_event


@pytest.mark.integration
def test_on_context_found_with_entity_type(app_request, app_registry_mock, app_context, jinja2_env_mock,
                                           context_found_event, jinja2_env,
                                           entity_type_mock):
    app_context.entity_type = entity_type_mock

    on_context_found(context_found_event)

    assert jinja2_env_mock is app_context.template_env
    assert hasattr(app_request, "override_renderer")
    assert app_request.override_renderer

    # ??
    with pytest.raises(TemplateNotFound):
        logger.critical("override renderer is %s", app_request.override_renderer)
        template = jinja2_env.get_template(app_request.override_renderer)


# problem is we lack ability to customize this "app_context" - it always comes with the mock
# @pytest.fixture
# def app_context(request, root_resource, entry_point_mock):
#     # this template wont exist...
#     return root_resource.sub_resource('app-context-%s' % request.param, entry_point_mock)
