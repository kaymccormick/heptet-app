import importlib
import json
import logging
import sys
from unittest.mock import MagicMock, Mock, PropertyMock

import pytest
from jinja2 import Environment, Template
from pyramid.config import Configurator
from pyramid.config.views import ViewDeriverInfo
from pyramid.registry import Registry
from pyramid.response import Response
from pyramid_jinja2 import IJinja2Environment
from pyramid_tm.tests import DummyRequest
from zope.interface.registry import Components

import email_mgmt_app
import email_mgmt_app.myapp_config
from context import FormContext, GeneratorContext
from db_dump import RelationshipSchema, ColumnInfo
from db_dump.info import MapperInfo, TypeInfo
from email_mgmt_app import get_root, Resource, ResourceManager, ResourceOperation, BaseView
from entity import EntityFormViewEntryPointGenerator
from entity import FormRelationshipMapper, RelationshipSelect
from entrypoint import EntryPoint
from form import Form
from impl import NamespaceStore, MapperWrapper, Separator
from myapp_config import TEMPLATE_ENV_NAME
from process import load_process_struct, AssetManager, ProcessContext
from tvars import TemplateVars
from viewderiver import entity_view

logger = logging.getLogger(__name__)

APP_PACKAGE = 'email_mgmt_app'


#
# DATA
#
@pytest.fixture
def webapp_settings():
    return {
        'sqlalchemy.url': 'sqlite:///:memory:',  # 'postgresql://flaskuser:FcQCPDM7%40RpRCsnO@localhost/email',
        'email_mgmt_app.secret': '9ZZFYHs5uo#ZzKBfXsdInGnxss2rxlbw',
        'email_mgmt_app.authsource': 'db',
        'email_mgmt_app.request_attrs': 'context, root, subpath, traversed, view_name, matchdict, virtual_root, virtual_root_path, exception, exc_info, authenticated_userid, unauthenticated_userid, effective_principals',
        'jinja2.directories': "email_mgmt_app/templates\nemail_mgmt_app\ntemplates\n.",
        'jinja2.autoescape': "false",
        'email_mgmt_app.jinja2.directories': "email_mgmt_app/templates\nemail_mgmt_app\ntemplates\n.",
        'email_mgmt_app.jinja2.autoescape': "false",

    }


_data = {'secondary': None, 'argument': 'email_mgmt_app.model.email_mgmt.Person', 'direction': 'MANYTOONE',
         'is_property': True, 'is_mapper': False, 'local_remote_pairs': [
        {'local': {'table': {'key': 'public_key'}, 'key': 'owner_id'},
         'remote': {'table': {'key': 'person'}, 'key': 'id'}}], 'mapper': {'local_table': {'key': 'person'}},
         'is_attribute': False, 'key': 'owner'}
_json = """
        {
          "secondary": null,
          "argument": "email_mgmt_app.model.email_mgmt.Person",
          "direction": "MANYTOONE",
          "is_property": true,
          "is_mapper": false,
          "local_remote_pairs": [
            {
              "local": {
                "table": {
                  "key": "public_key"
                },
                "key": "owner_id"
              },
              "remote": {
                "table": {
                  "key": "person"
                },
                "key": "id"
              }
            }
          ],
          "mapper": {
            "local_table": {
              "key": "person"
            }
          },
          "is_attribute": false,
          "key": "owner"
        }"""


@pytest.fixture
def my_json():
    return _json


@pytest.fixture
def my_data(my_json):
    d = json.loads(my_json)
    print(repr(d), file=sys.stderr)
    return d


#
# Primary application related fixtures
#
@pytest.fixture
def app_request(app_registry):
    # We'll use dummy request until we can't anymore
    request = DummyRequest()
    request.registry = app_registry
    return request


@pytest.fixture
def app_registry():
    return Components()


@pytest.fixture
def app_registry_mock(jinja2_env_mock):
    x = MagicMock(Registry)

    def _se(i, name):
        if i is IJinja2Environment and name == TEMPLATE_ENV_NAME:
            return jinja2_env_mock
        raise None

    x.queryUtility.side_effect = _se
    return x


@pytest.fixture
def entry_point_mock():
    mock = Mock(EntryPoint, name='entry_point')
    name = '_default'
    p = PropertyMock(return_value=name)
    type(mock).key = p
    type(mock).view_kwargs = PropertyMock(return_value=dict(view=lambda x, y: {}))
    type(mock).discriminator = PropertyMock(return_value=['entry_point', Separator, name])
    return mock


@pytest.fixture(params=["test"])
def app_context(request, root_resource, resource_manager, entry_point_mock):
    # this template wont exist...
    return root_resource.sub_resource('app-context-%s' % request.param, entry_point_mock)


#
# CONFIG
#
@pytest.fixture
def make_config():
    def _make_config(settings):
        return Configurator(settings=settings, package=APP_PACKAGE)

    return _make_config


@pytest.fixture
def config_mock():
    return MagicMock(Configurator())


@pytest.fixture
def config_fixture():
    config = Configurator(package="email_mgmt_app", root_package="email_mgmt_app")
    config.include(email_mgmt_app.myapp_config)
    logger.warning("config = %s", config)
    # _dump(config, name_prefix="config.", cb=lambda x, *args, **kwargs: print(x % args, file=sys.stderr))
    # config.commit()
    return config


#
# TEMPLATE ENVIRONMENT
#
@pytest.fixture
def make_jinja2_env(make_config):
    def _make_jinja2_env():
        config = make_config(
            {'email_mgmt_app.jinja2.directories': "email_mgmt_app/templates\ntemplates\nemail_mgmt_apps\n."})
        config.include('.template')
        config.add_jinja2_renderer(TEMPLATE_ENV_NAME, settings_prefix='email_mgmt_app.jinja2.', package=email_mgmt_app)
        return config

    return _make_jinja2_env


@pytest.fixture
def jinja2_env(make_jinja2_env, make_config):
    config = make_jinja2_env()
    config.commit()
    return config.registry.getUtility(IJinja2Environment, TEMPLATE_ENV_NAME)


@pytest.fixture
def jinja2_env_mock():
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


#

# Resource related fixtures
#
@pytest.fixture()
def root_resource(app_request):
    yield get_root(app_request)

    email_mgmt_app.reset_root(app_request)


@pytest.fixture
def resource_operation(view_test):
    return ResourceOperation('test_op', view_test, [])


@pytest.fixture
def make_resource(root_resource, entry_point_mock, resource_manager):
    def _make_resource(name):
        return Resource(resource_manager, name, root_resource, entry_point_mock)

    return _make_resource


@pytest.fixture
def resource_manager(config_fixture, entity_type_mock, mapper_wrapper_real):
    return ResourceManager(
        mapper_wrapper_real.key,
        title="",
        entity_type=entity_type_mock,
        mapper_wrapper=mapper_wrapper_real
    )


#
# ENTRY POINT
#
# @pytest.fixture
# def entry_point(mapper_wrapper_real, app_request, app_registry, jinja2_env_mock, resource_manager):
#     return EntryPoint(resource_manager, "domain_form", app_request, app_registry, mapper_wrapper=mapper_wrapper_real)


#
# Factories and builders
#
@pytest.fixture
def response_factory():
    return Response


#
# View-related
#

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
def view_baseview(make_resource, app_request):
    r = make_resource('view1')
    return BaseView(r, app_request)


#
# View derivers
#
@pytest.fixture
def view_deriver_info_mock():
    return MagicMock(name="view_deriver_info")


@pytest.fixture
def make_view_deriver_info():
    def _make_view_deriver_info(original_view, registry, package, predicates, exception_only, options):
        return ViewDeriverInfo(original_view, registry, package, predicates, exception_only, options)

    return _make_view_deriver_info


@pytest.fixture
def entity_view_deriver(view_test, make_view_deriver_info, app_registry, resource_operation):
    options = {'operation': resource_operation}
    di = make_view_deriver_info(view_test, app_registry, __name__, [], False, options)
    return entity_view(view_test, di)


@pytest.fixture
def entity_view_deriver_with_mocks(view_test, view_deriver_info_mock):
    return entity_view(view_test, view_deriver_info_mock)


#
# Entity-related
#
@pytest.fixture
def entity_type_mock():
    return MagicMock('entity_type')


@pytest.fixture
def mapper_info_mock():
    mock = MagicMock('mapper_info')
    mock.mock_add_spec(MapperInfo())
    return mock


@pytest.fixture
def mapper_info_real(mappers_real):
    return mappers_real[0]


@pytest.fixture
def mapper_wrapper_real(mapper_info_real):
    return MapperWrapper(mapper_info_real)


#
# NAMESPACE
#
@pytest.fixture
def root_namespace_store():
    return NamespaceStore("root")


@pytest.fixture(params=map(lambda x: "ns%d" % x, range(1, 10)))
def namespace_store(request):
    return NamespaceStore(request.param)


#
# TEMPLATES AND VARIABLES
#

@pytest.fixture
def make_template_vars():
    def _make_template_vars(**kwargs):
        return TemplateVars(**kwargs)

    return _make_template_vars


@pytest.fixture
def template_vars():
    return TemplateVars()


@pytest.fixture
def my_template_vars(make_template_vars):
    return make_template_vars(js_imports=[], js_stmts=[], ready_stmts=[])


#
# GENERATOR
#
@pytest.fixture
def make_generator_context(jinja2_env_mock, mapper_info_real, template_vars, root_namespace_store):
    def _make_generator_context(mapper=mapper_info_real, env=jinja2_env_mock, tvars=template_vars,
                                root=root_namespace_store):
        return GeneratorContext(mapper, tvars, FormContext, root, env)

    return _make_generator_context


@pytest.fixture
def generator_context_mock(make_generator_context):
    mock = MagicMock('generator_context_mock')
    mock.mock_add_spec(make_generator_context())
    return mock


@pytest.fixture
def my_gen_context(make_generator_context, jinja2_env, mapper_info_real, my_template_vars):
    return make_generator_context(mapper_info_real, jinja2_env, my_template_vars)


@pytest.fixture
def process_struct_real():
    return load_process_struct()


@pytest.fixture
def mappers_real(process_struct_real):
    return process_struct_real.mappers


@pytest.fixture
def my_relationship_info(relationship_schema, my_data):
    return relationship_schema.load(my_data)


@pytest.fixture
def relationship_schema():
    return RelationshipSchema()


#
# FORMS
#

@pytest.fixture
def my_relationship_select():
    return RelationshipSelect()


@pytest.fixture
def form_config_test(my_gen_context, process_struct_real):
    pass
    # organization = inspect(Domain).relationships.organization
    # map_column(organization, field_renderer.Select)
    # logger.warning("%s", get_column_map(organization))


@pytest.fixture
def make_form_context():
    def _make_form_context(generator_context, root_namespace_store, form):
        generator_context.form_context_factory()
        # return FormContext(generator_context, generator_context.template_env, root_namespace_store, form=form, relationship_field_mapper=FormRelationshipMapper)

    return _make_form_context


@pytest.fixture
def form_context_mock(make_form_context, generator_context_mock, root_namespace_store, my_form):
    mock = MagicMock('form_context_mock')
    mock.mock_add_spec(make_form_context(generator_context_mock, root_namespace_store, my_form))
    return mock


@pytest.fixture
def my_form(root_namespace_store):
    return Form('myform', root_namespace_store, outer_form=True)


@pytest.fixture
def my_form_context(my_gen_context, my_relationship_select, root_namespace_store):
    # mapper = FormRelationshipMapper(my_relationship_select) # fixme
    # we need to factor this thing away with a partial
    the_form = Form(namespace_id="test",
                    root_namespace=root_namespace_store,
                    namespace=None,  # can be None
                    outer_form=True)  # , form_action="./")

    return my_gen_context.form_context(relationship_field_mapper=FormRelationshipMapper, form=the_form)


@pytest.fixture
def entity_form_view_entry_point_generator(my_gen_context):
    return EntityFormViewEntryPointGenerator(my_gen_context)


@pytest.fixture
def entity_form_view_mock():
    return MagicMock('entity_form_view')


@pytest.fixture
def model_module():
    pkg = 'model.email_mgmt'
    if pkg in sys.modules:
        return sys.modules[pkg]

    return importlib.import_module(pkg)


@pytest.fixture(params=('test1', 'test2'))
def my_column_info(request):
    return ColumnInfo(TypeInfo(), request.param, request.param)


@pytest.fixture
def asset_manager():
    return AssetManager("tmpdir", mkdir=True)


@pytest.fixture
def asset_manager_mock():
    return Mock(AssetManager)


@pytest.fixture
def process_context_mock():
    return MagicMock(ProcessContext)
