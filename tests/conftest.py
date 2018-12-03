#
# Primary application related fixtures
#
from unittest.mock import MagicMock, Mock, PropertyMock

import pytest
from jinja2 import Environment, Template
from pyramid.registry import Registry
from pyramid.testing import DummyRequest
from pyramid_jinja2 import IJinja2Environment

import heptet_app
from heptet_app.myapp_config import TEMPLATE_ENV_NAME


@pytest.fixture
def app_registry_mock(jinja2_env_mock):
    """
    This mocks the registry and provides the primary instance we need. We
    could mock the registry and return a non-mock jinja2 env - that would be useful
    too.
    :param jinja2_env_mock:
    :return:
    """
    x = MagicMock(Registry, name="app_registry_mock")

    def _se(i, name):
        if i is IJinja2Environment and name == TEMPLATE_ENV_NAME:
            return jinja2_env_mock
        raise None

    x.queryUtility.side_effect = _se
    return x


#
# how do we want to 'select' the entry points for the request?
# through an 'add'?
#
@pytest.fixture
def app_request(app_registry_mock):
    """
    App request mock.
    :param app_registry_mock:
    :return:
    """
    request = DummyRequest()
    request.registry = app_registry_mock
    type(request).entry_points = PropertyMock()

    return request


@pytest.fixture
def jinja2_env_mock():
    """
    Mock the jinja2 env.
    :return:
    """
    mock = MagicMock(Environment, name='jinja2_env')
    # mock.mock_add_spec(Environment.__class__)
    # mock.mock_add_spec(['get_template'])
    _templates = {}

    def _get_template(name):
        if name in _templates:
            return _templates[name]
        tmock = Mock(Template)
        _templates[name] = tmock
        tmock.render.side_effect = lambda **kwargs: dict(**kwargs)
        return tmock

    mock.get_template.side_effect = _get_template
    mock._templates = lambda: _templates
    return mock


@pytest.fixture()
def root_resource(app_request):
    """
    Call the root factory and return the root resource. The root factory is hard-coded
    because it is always the same!
    :param app_request:
    :return:
    """
    heptet_app.reset_root(app_request)
    root = heptet_app.get_root(app_request)
    yield root
    heptet_app.reset_root(app_request)
    assert heptet_app.get_root(app_request) is not root

@pytest.fixture
def app_registry_mock(jinja2_env_mock):
    """
    This mocks the registry and provides the primary instance we need. We
    could mock the registry and return a non-mock jinja2 env - that would be useful
    too.
    :param jinja2_env_mock:
    :return:
    """
    x = MagicMock(Registry, name="app_registry_mock")

    def _se(i, name):
        if i is IJinja2Environment and name == TEMPLATE_ENV_NAME:
            return jinja2_env_mock
        raise None

    x.queryUtility.side_effect = _se
    return x

@pytest.fixture
def jinja2_env_mock():
    """
    Mock the jinja2 env.
    :return:
    """
    mock = MagicMock(Environment, name='jinja2_env')
    # mock.mock_add_spec(Environment.__class__)
    # mock.mock_add_spec(['get_template'])
    _templates = {}

    def _get_template(name):
        if name in _templates:
            return _templates[name]
        tmock = Mock(Template)
        _templates[name] = tmock
        tmock.render.side_effect = lambda **kwargs: dict(**kwargs)
        return tmock

    mock.get_template.side_effect = _get_template
    mock._templates = lambda: _templates
    return mock


from .fixtures import entry_point_mock,\
    process_context_mock,\
    entry_point_generator_mock,\
    asset_manager_mock,\
    make_entry_point,\
    process_context,\
    jinja2_env,\
    make_jinja2_env,\
    make_config,\
    asset_manager_mock_wraps_virtual,\
    virtual_asset_manager