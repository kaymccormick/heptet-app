import logging
from unittest.mock import MagicMock

import pytest
from db_dump.info import MapperInfo
from pyramid_tm.tests import DummyRequest

from email_mgmt_app.entity import EntityFormViewEntryPointGenerator, EntryPoint, FormRepresentationBuilder
from context import FormContext, GeneratorContext
from email_mgmt_app.impl import NamespaceStore, MapperWrapper
from email_mgmt_app.res import RootResource, Resource, ResourceManager
from email_mgmt_app.viewderiver import entity_view
from jinja2 import Environment
from pyramid.config import Configurator
from pyramid.response import Response

from tvars import TemplateVars

logger = logging.getLogger(__name__)


@pytest.fixture
def app_registry(app_request):
    return app_request.registry


@pytest.fixture()
def root_resource():
    return RootResource()


@pytest.fixture
def app_request():
    return DummyRequest()


@pytest.fixture(params=["test"])
def app_context(request, root_resource):
    return Resource(request.param, request)


@pytest.fixture
def response_factory():
    return Response


@pytest.fixture
def view_result(response_factory):
    return response_factory("")


@pytest.fixture
def view_test(app_context, app_request, view_result):
    def view_test(context, request):
        assert context is app_context
        assert request is app_request
        return view_result

    return view_test


@pytest.fixture
def view_deriver_info():
    return MagicMock(name="view_deriver_info")


@pytest.fixture
def entity_view_deriver(view_test, view_deriver_info):
    return entity_view(view_test, view_deriver_info)


@pytest.fixture
def config_fixture():
    return Configurator()


@pytest.fixture
def entity_type():
    return MagicMock('entity_type')


@pytest.fixture
def mapper_info():
    mock = MagicMock('mapper_info')
    mock.mock_add_spec(MapperInfo())
    return mock


@pytest.fixture
def mapper_wrapper(mapper_info):
    return MapperWrapper(mapper_info)


@pytest.fixture
def resource_manager(config_fixture, entity_type, mapper_wrapper):
    return ResourceManager(config_fixture, "", "", entity_type, mapper_wrapper)


@pytest.fixture
def root_namespace_store():
    return NamespaceStore("root")


@pytest.fixture(params=map(lambda x: "ns%d" % x, range(1, 10)))
def namespace_store(request):
    return NamespaceStore(request.param)


@pytest.fixture
def make_resource(root_resource, entity_type):
    def _make_resource(name):
        return Resource(name, root_resource, name, entity_type)

    return _make_resource


@pytest.fixture
def entry_point(mapper_wrapper, app_request, app_registry, jinja2_env):
    return EntryPoint("", app_request, app_registry, mapper_wrapper=mapper_wrapper, output_filename="tmp.out",
                      template=jinja2_env.get_template('entry_point.js.jinja2'))


@pytest.fixture
def entity_form_view_entry_point_generator(form_context, form_representation_builder, entry_point,
                                           entity_form_view_mock,
                                           ):
    return EntityFormViewEntryPointGenerator(form_context, form_representation_builder, entry_point,
                                             entity_form_view_mock,
                                             )


@pytest.fixture
def entity_form_view_mock():
    return MagicMock('entity_form_view')


@pytest.fixture
def jinja2_env():
    mock = MagicMock('jinja2_env')
    mock.mock_add_spec(Environment())
    return mock


@pytest.fixture
def template_vars():
    return TemplateVars()


@pytest.fixture
def generator_context(jinja2_env, mapper_info, template_vars):
    return GeneratorContext(mapper_info, jinja2_env, template_vars)


@pytest.fixture
def form_context(generator_context, root_namespace_store):
    return FormContext(generator_context, root_namespace_store)


@pytest.fixture
def form_representation_builder(form_context):
    return FormRepresentationBuilder(form_context)
