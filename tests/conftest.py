import importlib
import json
import logging
import sys
from typing import AnyStr
from unittest.mock import MagicMock, Mock, PropertyMock

import pytest
from jinja2 import Environment, Template
from lxml import html
from pyramid.config import Configurator
from pyramid.config.views import ViewDeriverInfo
from pyramid.registry import Registry
from pyramid.response import Response
from pyramid_jinja2 import IJinja2Environment
from pyramid_tm.tests import DummyRequest
from zope.interface.registry import Components

import email_mgmt_app
import email_mgmt_app.myapp_config
from db_dump import RelationshipSchema, ColumnInfo, LocalRemotePairInfo, TableColumnSpecInfo
from db_dump.info import MapperInfo, TypeInfo, TableInfo, RelationshipInfo
from email_mgmt_app import get_root, Resource, ResourceManager, ResourceOperation, BaseView, EntryPoint, \
    EntryPointGenerator
from email_mgmt_app.context import GeneratorContext, FormContext
from email_mgmt_app.entity import EntityFormViewEntryPointGenerator
from email_mgmt_app.entity import FormRelationshipMapper, RelationshipSelect
from email_mgmt_app.form import Form
from email_mgmt_app.impl import NamespaceStore, MapperWrapper, Separator
from email_mgmt_app.myapp_config import TEMPLATE_ENV_NAME
from email_mgmt_app.process import FileAssetManager, ProcessContext, AbstractAssetManager
from email_mgmt_app.process import VirtualAssetManager
from email_mgmt_app.process import load_process_struct
from email_mgmt_app.tvars import TemplateVars
from email_mgmt_app.viewderiver import entity_view
from tests import Property
from tests.common import MakeEntryPoint

logger = logging.getLogger(__name__)

APP_PACKAGE = 'email_mgmt_app'


#
# DATA
#
# fixme pull passwords from external
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


# what is this?
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
def app_request(app_registry_mock):
    # We'll use dummy request until we can't anymore
    request = DummyRequest()
    request.registry = app_registry_mock
    try:
        yield request
    except:
        for x in app_registry_mock.mock_calls:
            print(str(x), file=sys.stderr)


@pytest.fixture
def app_registry():
    """
    See also app_registry_mock.
    :return:
    """
    return Components()


@pytest.fixture
def app_registry_mock(jinja2_env_mock):
    """
    This mocks the registry and provides the primary instance we need. We
    could mock the registry and return a non-mock jinja2 env - that would be useful
    too.
    :param jinja2_env_mock:
    :return:
    """
    x = MagicMock(Registry)

    def _se(i, name):
        if i is IJinja2Environment and name == TEMPLATE_ENV_NAME:
            return jinja2_env_mock
        raise None

    x.queryUtility.side_effect = _se
    return x


@pytest.fixture
def entry_point_mock():
    """
    entry_point_mock pytest fixture
    :return:
    """
    mock = Mock(EntryPoint)  # , name='entry_point')  # do we need to name this??
    # this is sort of a "hack" to get it to work (_default)
    default = '_default'
    type(mock).key = PropertyMock(return_value=default)
    type(mock).view_kwargs = PropertyMock(return_value=dict(view=lambda x, y: {}))
    type(mock).discriminator = PropertyMock(return_value=['entry_point', Separator, default])
    type(mock).mapper = PropertyMock()
    return mock


@pytest.fixture(params=["test"])
def app_context(request, root_resource, resource_manager, entry_point_mock):
    # this template wont exist...
    return root_resource.sub_resource('app-context-%s' % request.param, entry_point_mock)


#
# CONFIG
#  * make_config
@pytest.fixture
def make_config():
    def _make_config(settings):
        return Configurator(settings=settings, package=APP_PACKAGE)

    return _make_config


# CONFIG
#  * config_mock
@pytest.fixture
def config_mock():
    """
    Random configurator mock, I am not sure why this would be useful at all.
    :return:
    """
    return MagicMock(Configurator())


# CONFIG
#  * config_fixture
@pytest.fixture
def config_fixture():
    """
    This is our basic "config fixture" for the application. Includes "myapp_config" which
    maybe hopefully provides all of our configuration? Part test, part experiment.
    :return:
    """
    config = Configurator(package="email_mgmt_app", root_package="email_mgmt_app")
    config.include(email_mgmt_app.myapp_config)
    logger.warning("config = %s", config)
    # _dump(config, name_prefix="config.", cb=lambda x, *args, **kwargs: print(x % args, file=sys.stderr))
    config.commit()
    return config


#
# TEMPLATE ENVIRONMENT
#
@pytest.fixture
def make_jinja2_env(make_config):
    """
    Factory fixture to make "jinja2 environments"
    :param make_config:
    :return:
    """

    def _make_jinja2_env():
        # FIXME move this somewhere else
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


#
# RESOURCES
#
@pytest.fixture()
def root_resource(app_request):
    """
    Call the root factory and return the root resource. The root factory is hard-coded
    because it is always the same!
    :param app_request:
    :return:
    """
    email_mgmt_app.reset_root(app_request)
    root = get_root(app_request)
    yield root
    email_mgmt_app.reset_root(app_request)
    assert get_root(app_request) is not root


@pytest.fixture
def make_resource(entry_point_mock, resource_manager):
    def _make_resource(name):
        return Resource(name, root_resource, entry_point_mock)

    return _make_resource


# investigate this
@pytest.fixture
def resource_operation(view_test):
    return ResourceOperation('test_op', view_test, [])


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
def make_entity_view_deriver(resource_operation_mock, app_registry_mock):
    def _make_entity_view_deriver(view, info):
        return entity_view(view, info)

    return _make_entity_view_deriver


# what is this doing, exacltY?
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
def element_mock():
    element = html.Element('elem')
    m = MagicMock(element)
    return m


@pytest.fixture
def mapper_info_mock(local_remote_pair_info_mock):
    top_mock = MagicMock(MapperInfo, name='mapper_info')

    type(top_mock).entity = PropertyMock()

    col_info_mock = MagicMock(ColumnInfo, name='col_info')
    type(col_info_mock).key = PropertyMock(name='key', return_value='child_id')
    type(col_info_mock).name = PropertyMock(name='name', return_value='child_id')
    type(col_info_mock).table = PropertyMock(name='table', return_value='table1')
    type(col_info_mock).__visit_name__ = PropertyMock(return_value='column')
    type_mock = MagicMock(name='type')


    type(col_info_mock).type = PropertyMock(name='type', return_value=type_mock)

    #type(m).type = PropertyMock(return_value=TypeInfo())
    type(top_mock).columns = PropertyMock(list, return_value=[col_info_mock])

    class LocalTableMock(MagicMock):
        pass

    magic_mock = MagicMock(name='local_table')
    type(magic_mock).key = PropertyMock(name='key', return_value='table1')
    property_mock = PropertyMock(TableInfo, return_value=magic_mock)
    type(top_mock).local_table = property_mock

    rel_mock = MagicMock(RelationshipInfo, name='relationship_info')
    type(rel_mock).key = PropertyMock(return_value='key1')
    pair_mock = local_remote_pair_info_mock
    type(rel_mock).local_remote_pairs = PropertyMock(list, return_value=[pair_mock])
    type(rel_mock).direction = PropertyMock(return_value='MANYTOONE')
    type(rel_mock).argument = PropertyMock()
    type(rel_mock).secondary = PropertyMock(return_value=None)
    type(rel_mock).mapper = PropertyMock()

    rel_prop_mock = PropertyMock(list, name='relationships', return_value=[rel_mock])
    type(top_mock).relationships = rel_prop_mock

    # mock.local_table.key.side_effect = 'table1x'
    return top_mock


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


@pytest.fixture
def template_vars_wrapped():
    return TemplateVars()


@pytest.fixture
def template_vars_mock(template_vars_wrapped):
    mock = MagicMock(wraps=template_vars_wrapped)
    mock.__setitem__ = MagicMock(TemplateVars.__setitem__, wraps=template_vars_wrapped.__setitem__)
    logger.critical("%r", mock)
    return mock


#
# GENERATOR
#
@pytest.fixture
def wrap_form_context_factory():
    def _wrap_form_context_factory(*args, **kwargs):
        c = FormContext(*args, **kwargs)
        return MagicMock(wraps=c)

    return _wrap_form_context_factory

@pytest.fixture
def make_generator_context(jinja2_env_mock, template_vars, root_namespace_store, wrap_form_context_factory):
    def _make_generator_context(entry_point, mapper=None, env=jinja2_env_mock, tvars=template_vars,
                                root=root_namespace_store):
        return GeneratorContext(entry_point, tvars, wrap_form_context_factory, root, env, mapper_info=mapper)

    return _make_generator_context


@pytest.fixture
def generator_context_mock(make_generator_context, jinja2_env_mock, template_vars_mock, mapper_info_mock,
                           form_context_mock):
    mock = MagicMock(GeneratorContext)
    type(mock).template_env = PropertyMock(return_value=jinja2_env_mock)
    type(mock).template_vars = PropertyMock(return_value=template_vars_mock)
    type(mock).mapper = PropertyMock(return_value=mapper_info_mock)
    logger.critical("%r", mock)
    logger.critical("form_ctx_m = %r", form_context_mock)
    mock.form_context().return_value = form_context_mock

    return mock


@pytest.fixture
def my_gen_context(
        make_generator_context,
        jinja2_env,
        mapper_info_real,
        my_template_vars,
        make_entry_point
):
    entry_point = make_entry_point(manager, key, generator, mapper_info_real)
    return make_generator_context(entry_point, jinja2_env, my_template_vars)


@pytest.fixture
def process_struct_real():
    return load_process_struct()


@pytest.fixture
def mappers_real(process_struct_real):
    assert process_struct_real.mappers
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
def wrap_form_factory():
    def _wrap_form_factory(*args, **kwargs):
        form = Form(*args, **kwargs)
        mock = MagicMock(wraps=form)
        return mock
    return _wrap_form_factory


# this makes a form context from a geneerator context which is not what we want
@pytest.fixture
def make_form_context(jinja2_env_mock, template_vars_mock, root_namespace_store, wrap_form_factory):
    def _make_form_context(template_env=jinja2_env_mock, template_vars=template_vars_mock, root_namespace=root_namespace_store,
                           namespace=None, form=None, mapper_info=None):
        return FormContext(template_env, template_vars, root_namespace, namespace, relationship_field_mapper=FormRelationshipMapper,
                    form=form, mapper_info=mapper_info,form_factory=wrap_form_factory)

    return _make_form_context


@pytest.fixture
def form_mock():
    mock = MagicMock(Form)
    mock.get_html_id().get_id.return_value = 'html_id'
    mock.get_html_form_name().get_id.return_value = 'form_name'
    return mock


@pytest.fixture
def form_context_mock(make_form_context, root_namespace_store, my_form, jinja2_env_mock, template_vars_mock, form_mock):
    mock = MagicMock(FormContext)
    type(mock).template_env = PropertyMock(return_value=jinja2_env_mock)
    type(mock).template_vars = PropertyMock(return_value=template_vars_mock)
    type(mock).nest_level = PropertyMock(return_value=0)
    type(mock).form = PropertyMock(return_value=form_mock)
    type(mock).extra = PropertyMock()
    # type(mock).
    # mock.mock_add_spec(make_form_context(generator_context_mock, root_namespace_store, my_form))
    return mock


@pytest.fixture
def my_form(root_namespace_store):
    return Form('myform', root_namespace_store, outer_form=True)


@pytest.fixture
def my_form_context(make_generator_context, my_relationship_select, root_namespace_store, make_entry_point,
                    resource_manager_mock, entry_point_mock):
    # mapper = FormRelationshipMapper(my_relationship_select) # fixme
    # we need to factor this thing away with a partial
    manager = resource_manager_mock
    key = 'test1'
    entry_point = entry_point_mock  # make_entry_point(manager, key)
    my_gen_context = make_generator_context(entry_point)
    the_form = Form(namespace_id="test",
                    root_namespace=root_namespace_store,
                    namespace=None,  # can be None
                    outer_form=True)  # , form_action="./")

    return my_gen_context.form_context(relationship_field_mapper=FormRelationshipMapper, form=the_form)


@pytest.fixture
def entity_form_view_mock():
    return MagicMock('entity_form_view')


@pytest.fixture
def model_module():
    pkg = 'email_mgmt_app.model.email_mgmt'
    if pkg in sys.modules:
        return sys.modules[pkg]

    return importlib.import_module(pkg)


@pytest.fixture(params=('test1', 'test2'))
def my_column_info(request):
    return ColumnInfo(TypeInfo(), request.param, request.param)


@pytest.fixture
def asset_manager():
    raise TypeError
    return FileAssetManager("tmpdir", mkdir=True)


@pytest.fixture
def make_asset_manager():
    def _make_asset_manager(dir, mkdir=None):
        if mkdir is None:
            return FileAssetManager(dir)
        else:
            return FileAssetManager(dir, mkdir)

    return _make_asset_manager


@pytest.fixture
def asset_manager_mock_wraps_virtual():
    return MagicMock(wraps=VirtualAssetManager())


@pytest.fixture
def asset_manager_mock():
    return MagicMock(AbstractAssetManager)


@pytest.fixture
def process_context_mock():
    return MagicMock(ProcessContext)


@pytest.fixture
def make_resource_manager():
    def _make_resource_manager(*args, **kwargs):
        return ResourceManager(*args, **kwargs)


@pytest.fixture
def mapper_wrapper_mock():
    mock = MagicMock(MapperWrapper)
    return mock


@pytest.fixture
def make_entry_point() -> MakeEntryPoint:
    """
    Returns a function which takes arguments manager, key, generator, mapper_wrapper
    :return:
    """

    def _make_entry_point(key, manager=None, mapper=None):
        # i dont like having to pass manager!
        return EntryPoint(key, manager, mapper=mapper)

    return _make_entry_point


@pytest.fixture
def resource_manager_mock():
    return MagicMock(ResourceManager)


@pytest.fixture
def make_entity_form_view_entry_point_generator():
    def _make_entity_form_view_entry_point_generator(registry, ctx):
        return MagicMock(EntityFormViewEntryPointGenerator)

    return _make_entity_form_view_entry_point_generator


@pytest.fixture
def resource_operation_mock():
    return MagicMock(ResourceOperation)


# BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
#
# RESET_SEQ = "\\033[0m"
# COLOR_SEQ = "\\033[1;%dm"
# BOLD_SEQ = "\\033[1m"
#
# from lxml.builder import E
# xml = E.entrypoint(dict(manager=repr(entry_point_1.manager)))
# from lxml import etree
# print(etree.tostring(xml, pretty_print=True), file=sys.stderr)
#
# s = textwrap.fill(repr(entry_point_1), 120)
# s = re.sub('(?:\s|^)(\S+)\(', BOLD_SEQ + '\\1(' + RESET_SEQ, s)
# s = re.sub('([\(,\s]?\s*)([^=\s]+)(\s*)=', '\\1' + (COLOR_SEQ % (30 + 64)) + '\\2' + RESET_SEQ + '\\3=', s)
# print(s, file=sys.stderr)#logger.critical("%s", textwrap.fill(s, width=120, subsequent_indent="  "))
# logger.critical("%r", entry_point_1.discriminator)

@pytest.fixture
def entry_point_generator_mock():
    return MagicMock(EntryPointGenerator)


@pytest.fixture
def process_struct_basic_model():
    return load_process_struct(
        json_str="""{"tables": [], "mappers": [{"columns": [{"table": {"key": "test1"}, "name": "id", "foreign_keys": [], "key": "id", "type_": {"python_type": "builtins.int"}, "visit_name": "column"}, {"table": {"key": "test1"}, "name": "child_id", "foreign_keys": [{"visit_name": "foreign_key", "column": {"table": {"key": "child"}, "key": "id"}}], "key": "child_id", "type_": {"python_type": "builtins.int"}, "visit_name": "column"}], "entity": "db_dump.model.Test1", "primary_key": [{"type": {"python_type": "builtins.int"}, "table": "test1", "column": "id"}], "relationships": [{"is_attribute": false, "is_property": true, "secondary": null, "direction": "MANYTOONE", "mapper": {"local_table": {"key": "child"}}, "is_mapper": false, "argument": "db_dump.model.Child", "local_remote_pairs": [{"local": {"type_": {"python_type": "builtins.int"}, "table": {"key": "test1"}, "key": "child_id"}, "remote": {"type_": {"python_type": "builtins.int"}, "table": {"key": "child"}, "key": "id"}}], "key": "child"}], "local_table": {"key": "test1"}}, {"columns": [{"table": {"key": "child"}, "name": "id", "foreign_keys": [], "key": "id", "type_": {"python_type": "builtins.int"}, "visit_name": "column"}], "entity": "db_dump.model.Child", "primary_key": [{"type": {"python_type": "builtins.int"}, "table": "child", "column": "id"}], "relationships": [], "local_table": {"key": "child"}}], "generation": {"created": "2018-09-16T23:52:08.348156+00:00", "config_vars": {}, "python_version": "3.7.0", "system_alias": "('Windows', '10', '10.0.17134')"}}""")


class MapperMock(MagicMock):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)


@pytest.fixture
def monkeypatch_form(monkeypatch):
    with monkeypatch.context() as mp:
        form_orig = email_mgmt_app.form.Form.__new__

        def _form(cls,
                  namespace_id,  # this is used to make a namespace if not provided? messy!! what do we pass here ?!?!
                  root_namespace,
                  namespace: NamespaceStore = None,
                  outer_form=False, attr={}) -> None:
            form__ = form_orig(cls)
            form__.__init__(namespace_id, root_namespace, namespace, outer_form, attr)
            return MagicMock(wraps=form__)

        monkeypatch.setattr(email_mgmt_app.form.Form, "__new__", _form)
        yield True



class ElementMock(MagicMock):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def __repr__(self):
        return repr(html.tostring(self).decode('utf-8'))


@pytest.fixture
def make_element_mock():
    def _make_element_mock(element):
        mock1 = ElementMock(wraps=element, name="<%s>" % element.tag)

        mock1.append.return_value = None
        mock1.append.side_effect = lambda x: element.append(x._mock_wraps)
        property_any_str_ = Property[AnyStr](element, 'text')
        prop_mock = PropertyMock(wraps=property_any_str_)
        type(mock1).text = prop_mock
        return mock1

    return _make_element_mock


@pytest.fixture
def monkeypatch_html(monkeypatch, wrap_make_html, make_element_mock):
    monkeypatch.setattr(html, "Element", wrap_make_html)

    orig_tostring = html.tostring

    def _tostring(element, **kwargs):
        return orig_tostring(element._mock_wraps, **kwargs)

    orig_fromstring = html.fromstring

    def _fromstring(string, **kwargs):
        return make_element_mock(orig_fromstring(string, **kwargs))

    monkeypatch.setattr(html, "tostring", _tostring)
    monkeypatch.setattr(html, "fromstring", _fromstring)


@pytest.fixture
def wrap_make_html(make_element_mock):
    factory = html.Element

    def _wrap_make_html(*args, **kwargs):
        if len(args) >= 2:
            attr = args[1]
            keys = list(attr.keys())
            for key in keys:
                if not isinstance(attr[key], str):
                    attr[key]= str(attr[key])

        elem = factory(*args, **kwargs)

        return make_element_mock(elem)

    return _wrap_make_html


@pytest.fixture
def local_remote_pair_info_mock():
    m = MagicMock(LocalRemotePairInfo)
    local = MagicMock(TableColumnSpecInfo, wraps=TableColumnSpecInfo(table='table1', column='child_id'))
    type(local).table = PropertyMock(return_value='table1')
    type(local).column = PropertyMock(return_value='child_id')

    type(m).local = local
    remote = MagicMock(TableColumnSpecInfo)
    type(m).remote = remote
    m.__iter__.return_value = [local, remote]
    return m
