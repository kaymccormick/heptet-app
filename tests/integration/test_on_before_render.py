import logging
from unittest.mock import MagicMock, PropertyMock

import pytest
from jinja2 import TemplateNotFound
from pyramid.events import BeforeRender

from heptet_app.myapp_config import on_before_render

logger = logging.getLogger(__name__)

@pytest.fixture
def on_before_render_event(config_fixture):
    app = config_fixture.make_wsgi_app()
    environ = {}
    ctx = app.request_context(environ)
    request = ctx.begin()
    event = MagicMock(wraps=BeforeRender(request), name='before_render_event')
    # type-wide property mock, okay for request of course
    type(event).request = PropertyMock(return_value=request)
    return event

def test_on_before_render(on_before_render_event, caplog):
    caplog.set_level(logging.DEBUG)
    on_before_render(on_before_render_event)
