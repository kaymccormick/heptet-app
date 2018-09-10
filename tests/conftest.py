import builtins
import json
import logging
import sys
import types
from typing import Callable
from unittest.mock import MagicMock, Mock

import pytest
from db_dump.info import MapperInfo
from pyramid_tm.tests import DummyRequest
from zope.interface.registry import Components

import email_mgmt_app.myapp_config
from email_mgmt_app.entity import EntityFormViewEntryPointGenerator, EntryPoint
from email_mgmt_app.context import FormContext, GeneratorContext
from email_mgmt_app.impl import NamespaceStore, MapperWrapper
from res import RootResource, Resource, ResourceManager
from email_mgmt_app.viewderiver import entity_view
from jinja2 import Environment, Template
from pyramid.config import Configurator
from pyramid.response import Response

from email_mgmt_app.tvars import TemplateVars
from email_mgmt_app.form import Form
from email_mgmt_app.myapp_config import load_process_struct
from email_mgmt_app.entity import FormRelationshipMapper, RelationshipSelect

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
    config = Configurator(package="email_mgmt_app", root_package="email_mgmt_app")
    config.include(email_mgmt_app.myapp_config)
    logger.warning("config = %s", config)

    def _dump(v, lineprefix=None, nameprefix="", depth=0, cb: Callable = None, recurse=True):
        if lineprefix is None:
            lineprefix = "  " * depth

        vv = None
        if isinstance(v, types.ModuleType):
            vv = "<module '%s'>" % v.__name__
        if vv is None:
            vv = str(v)
        cb("%s%s = %s", lineprefix, nameprefix[0:-1], vv)
        if depth >= 5 or not recurse:
            return
        if isinstance(v, types.ModuleType):
            pass  # cb("%s: module %s", lineprefix, v)
        elif isinstance(v, Components):
            for x in v.registeredUtilities():
                _dump(x, None, "%s%s." % (nameprefix, "utility"), depth + 1, cb, recurse=False)
            #     _dump(x, None, "%s%s." % (nameprefix, "utility"), depth + 1, cb)
            pass
        elif hasattr(v, "__dict__"):
            for x, y in v.__dict__.items():
                if not x.startswith('_'):
                    # cb("%s%s%s = %s", lineprefix, nameprefix, x, y)
                    _dump(y, nameprefix="%s%s." % (nameprefix, x), depth=depth + 1, cb=cb)
        else:
            return

    _dump(config, nameprefix="config.", cb=lambda x, *args, **kwargs: print(x % args, file=sys.stderr))
    config.commit()
    return config


@pytest.fixture
def entity_type():
    return MagicMock('entity_type')


@pytest.fixture
def mapper_info_mock():
    mock = MagicMock('mapper_info')
    mock.mock_add_spec(MapperInfo())
    return mock


@pytest.fixture
def mapper_info(mappers):
    return mappers[0]


@pytest.fixture
def mapper_wrapper(mapper_info):
    return MapperWrapper(mapper_info)


@pytest.fixture
def resource_manager(config_fixture, entity_type, mapper_wrapper):
    return ResourceManager(config_fixture, mapper_wrapper.key, title="", entity_type=entity_type, mapper_wrapper=mapper_wrapper)


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
def entity_form_view_entry_point_generator(my_gen_context):
    return EntityFormViewEntryPointGenerator(my_gen_context)


@pytest.fixture
def entity_form_view_mock():
    return MagicMock('entity_form_view')


@pytest.fixture
def jinja2_env():
    mock = MagicMock(Environment)
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


@pytest.fixture
def make_template_vars():
    def _make_template_vars(**kwargs):
        return TemplateVars(**kwargs)

    return _make_template_vars


@pytest.fixture
def template_vars():
    return TemplateVars()


@pytest.fixture
def make_generator_context(jinja2_env, mapper_info, template_vars, root_namespace_store):
    def _make_generator_context(mapper=mapper_info, env=jinja2_env, tvars=template_vars, root=root_namespace_store):
        return GeneratorContext(mapper, env, tvars, FormContext, root)

    return _make_generator_context


@pytest.fixture
def make_form_context():
    def _make_form_context(generator_context, root_namespace_store, form):
        generator_context.form_context_factory()
        # return FormContext(generator_context, generator_context.template_env, root_namespace_store, form=form, relationship_field_mapper=FormRelationshipMapper)

    return _make_form_context


@pytest.fixture
def generator_context_mock(make_generator_context):
    mock = MagicMock('generator_context_mock')
    mock.mock_add_spec(make_generator_context())
    return mock


@pytest.fixture
def form_context_mock(make_form_context, generator_context_mock, root_namespace_store, my_form):
    mock = MagicMock('form_context_mock')
    mock.mock_add_spec(make_form_context(generator_context_mock, root_namespace_store, my_form))
    return mock


@pytest.fixture
def my_form(root_namespace_store):
    return Form('myform', root_namespace_store, outer_form=True)


@pytest.fixture
def my_form_context(my_gen_context):
    mapper = FormRelationshipMapper()
    return my_gen_context.form_context(mapper)


@pytest.fixture
def my_gen_context(make_generator_context, jinja2_env, mapper_info, my_template_vars):
    return make_generator_context(mapper_info, jinja2_env, my_template_vars)


@pytest.fixture
def my_template_vars(make_template_vars):
    return make_template_vars(js_imports=[], js_stmts=[], ready_stmts=[])


@pytest.fixture
def process_struct():
    return load_process_struct()


@pytest.fixture
def mappers(process_struct):
    return process_struct.mappers


@pytest.fixture
def my_relationship_select(my_form_context, my_relationship_info):
    fm = my_form_context.copy()
    fm.current_element = my_relationship_info
    return RelationshipSelect(fm)


@pytest.fixture
def my_relationship_info(relationship_schema, my_data):
    return relationship_schema.load(my_data)


@pytest.fixture
def relationship_schema():
    return RelationshipSchema()


@pytest.fixture
def my_data(my_json):
    d = json.loads(my_json)
    print(repr(d), file=sys.stderr)
    return d


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
def webapp_settings():
    return {
        'sqlalchemy.url': 'sqlite:///:memory:',  # 'postgresql://flaskuser:FcQCPDM7%40RpRCsnO@localhost/email',
        'email_mgmt_app.secret': '9ZZFYHs5uo#ZzKBfXsdInGnxss2rxlbw',
        'email_mgmt_app.authsource': 'db',
        'email_mgmt_app.request_attrs': 'context, root, subpath, traversed, view_name, matchdict, virtual_root, virtual_root_path, exception, exc_info, authenticated_userid, unauthenticated_userid, effective_principals',
        'email_mgmt_app.jinja2_loader_template_path': 'email_mgmt_app/templates:email_mgmt_app',
    }