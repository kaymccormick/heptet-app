import logging
from unittest.mock import MagicMock

import pytest
from pyramid_tm.tests import DummyRequest

from impl import NamespaceStore
from pyramid.config import Configurator
from pyramid.response import Response
from res import RootResource, Resource, ResourceManager
from viewderiver import entity_view

logger = logging.getLogger(__name__)


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
def mapper_wrapper():
    return MagicMock('mapper_wrapper')


@pytest.fixture
def resource_manager(config_fixture, entity_type, mapper_wrapper):
    return ResourceManager(config_fixture, "", "", entity_type, mapper_wrapper)

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
