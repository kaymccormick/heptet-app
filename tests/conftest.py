import logging
from unittest.mock import MagicMock

import pytest
from db_dump.info import MapperInfo
from pyramid_tm.tests import DummyRequest

from entity import EntityFormViewEntryPointGenerator, EntryPoint, FormRepresentationBuilder, FormContext
from impl import NamespaceStore, MapperWrapper
from pyramid.config import Configurator
from pyramid.response import Response
from res import RootResource, Resource, ResourceManager
from viewderiver import entity_view
from zope.component import getGlobalSiteManager

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
def entry_point(mapper_wrapper, app_request, app_registry):
    return EntryPoint("", app_request, app_registry, mapper_wrapper=mapper_wrapper)


@pytest.fixture
def entity_form_view():
    return MagicMock('entity_form_view')


@pytest.fixture
def jinja2_env():
    return MagicMock('jinja2_env')

@pytest.fixture
def form_context(jinja2_env, app_registry, mapper_info, root_namespace_store):
    return FormContext(jinja2_env, app_registry, mapper_info=mapper_info, root_namespace=root_namespace_store)

@pytest.fixture
def form_representation_builder(form_context):
    return FormRepresentationBuilder(form_context)

