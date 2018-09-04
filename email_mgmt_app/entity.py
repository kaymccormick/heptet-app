import json
import logging
from dataclasses import dataclass, fields, field
from typing import TypeVar, Generic

import stringcase
from db_dump.info import MapperInfo, RelationshipInfo, IRelationshipInfo

from jinja2 import Template

from email_mgmt_app.form import *
from email_mgmt_app.entrypoint import *
from email_mgmt_app.interfaces import *
from pyramid.config import Configurator
from pyramid.interfaces import IRendererFactory
from pyramid.request import Request
from pyramid.response import Response
from sqlalchemy.orm.base import MANYTOONE

from email_mgmt_app.model.meta import Base
from email_mgmt_app.util import render_template
from email_mgmt_app.view import BaseView
from pyramid.util import DottedNameResolver
from pyramid_jinja2 import IJinja2Environment
from email_mgmt_app.template import TemplateVariable

logger = logging.getLogger(__name__)


class IFormContext(Interface):
    pass


class IFormRelationshipMapper(Interface):
    def map_relationship(rel):
        pass


@adapter(IRelationshipInfo, IFormContext)
@implementer(IFormRelationshipMapper)
class FormRelationshipMapper:
    def __init__(self, rel, context) -> None:
        self._rel = rel
        self._context = context

    def map_relationship(self):
        context = self._context
        rel = self._rel
        prefix = context.prefix
        request = context.request
        nest_level = context.nest_level

        js_stmts_col = request.registry.queryUtility(ICollector, 'js_stmts')
        if js_stmts_col:
            js_stmts_col.add_value('// %s' % rel)

        logger.debug("Encountering relationship %s", rel)
        assert rel.direction
        if rel.direction.upper() != 'MANYTOONE':
            return ""

        logger.debug("Processing relationship %s", rel)

        #
        # decide here what control to use . right now we default to select.
        #
        select = request.registry.getAdapter(rel, IRelationshipSelect)
        select.set_context(context)
        select_html = select.get_select()
        logger.debug("select html is %s", select_html)
        assert select_html
        return select_html


@dataclass
class Templates:
    label: str = "templates/entity/label.jinja2"
    rel_select_option: str = "templates/entity/rel_select_option.jinja2"
    rel_select: str = "templates/entity/rel_select.jinja2"
    modal: str = 'templates/entity/modal.jinja2'
    field: str = "templates/entity/field.jinja2"
    field_relationship: str = "templates/entity/field_relationship.jinja2"
    form: str = "templates/entity/form.jinja2"
    form_enclosure: str = "templates/entity/form_enclosure.jinja2"
    form_wrapper: str = "templates/entity/form_wrapper.jinja2"
    button_create_new: str = "templates/entity/button_create_new.jinja2"
    button_create_new_click_js: str = "templates/entity/button_create_new_js.jinja2"
    collapse: str = "templates/entity/collapse.jinja2"


templates = Templates()
typemap = {'': ['text']}
renderers = {}


def template_source(request, template_name):
    f = request.registry.queryUtility(IRendererFactory, '.jinja2')
    source = f.environment.loader.get_source({}, template_name)
    return source[0]

    #
    # mapper_key = mapper['mapper_key']
    # logger.info("Rendering entity form for %s" % mapper_key)
    # d = {'form_contents': '', 'header': stringcase.sentencecase(mapper_key),
    #      'header2': mapper['doc'] or '',
    #      'modals': ''}
    #
    # suppress = {}
    #
    # alchemy: AlchemyInfo
    # alchemy = request.registry.email_mgmt_app.alchemy
    #
    # assert mapper
    #
    # # TODO - re-implement using dictionary loaded via json
    #
    # # for pkey_col in inspect.primary_key:
    # #     suppress[pkey_col.key] = True
    #
    # readycode = ''
    #
    # for rel in mapper['relationships']:
    #     if rel['direction'] == MANYTOONE:
    #         continue
    #     arg = rel['argument']
    #     rel_o = arg
    #
    #     pairs = rel['local_remote_pairs']
    #     local = pairs[0]['local']
    #     remote = pairs[0]['remote']
    #
    #     key_ = rel['key']
    #     label_contents = stringcase.sentencecase(key_)
    #     if isinstance(rel_o, Base):
    #         entities = request.dbsession.query(rel_o).all()
    #     else:
    #         entities = []
    #
    #     select_contents = ''
    #
    #     modal_id = 'modal_%s%s' % (prefix, key_)
    #     buttons = ''
    #     collapse = ''
    #     select_id = 'select_%s%s' % (prefix, key_)
    #     button_id = 'button_%s%s' % (prefix, key_)
    #
    #     if nest_level < 1:
    #         #logger.warning("keys = %s", repr(request.registry.email_mgmt_app.mappers.keys()))
    #         do_modal = False
    #
    #         key = rel['key']
    #         entity_form = render_entity_form\
    #             ( request                           ,
    #               alchemy.mappers[remote['table']]     ,
    #               outer_vars                        ,
    #               nest_level + 1                    ,
    #               do_modal=do_modal                 ,
    #               prefix="%s%s." % (prefix, key),
    #               )
    #
    #         if do_modal:
    #             d['modals'] = d['modals'] + render_template \
    #                 (request, templates.modal,
    #                  {
    #                      'is_modal': True,
    #                      'modal_id': modal_id, 'modal_title': label_contents,
    #                      'modal_body': entity_form
    #                  })
    #             # buttons = buttons + render_template(request, templates.button_create_new_modal, { 'modal_id': modal_id })
    #         else:
    #             collapse_id = 'collapse_%s' % key
    #             collapse = render_template(request, templates.collapse, {'collapse_contents': entity_form,
    #                                                                      'collapse_id': collapse_id})
    #
    #             readycode = readycode + render_template(request, templates.button_create_new_click_js,
    #                                                     { 'button_id': button_id,
    #                                                       'collapse_id': collapse_id,
    #                                                       'select_id': select_id })
    #
    #             buttons = buttons + render_template \
    #                 (request,
    #                  templates.button_create_new,
    #                  {'button_id': button_id,
    #                   'select_id': select_id,
    #                   'collapse_id': collapse_id})
    #
    #
    #
    #     select_contents = select_contents + \
    #                       render_template(request, templates.rel_select_option,
    #                                       {'option_value': 0,
    #                      'option_contents': "None"})
    #     select_contents = select_contents + \
    #                       render_template(request, templates.rel_select_option,
    #                                       {'option_value': -1,
    #                      'option_contents': "New"})
    #
    #     for entity in entities:
    #         select_contents = select_contents + \
    #                           render_template(request, templates.rel_select_option,
    #                                           {'option_value': entity.__dict__[remote.name],
    #                                            'option_contents': entity.display_name})
    #
    #
    #     rel_select = render_template(request, templates.rel_select, {'select_name': prefix + local['column'],
    #                                                                  'select_id': select_id,
    #                                                                  'select_value': None,
    #                                                                  'select_contents': select_contents,
    #                                                                  'buttons': buttons,
    #
    #                                                                  'collapse': collapse,
    #                                                                  })
    #     d['form_contents'] = d['form_contents'] + render_template(request, templates.field_relationship,
    #                                                               {'input_html': rel_select,
    #                                                              'label_html': label_html(request, select_id,
    #                                                                                       label_contents),
    #                                                              'collapse': collapse,
    #                                                              'help': rel['doc']})
    #
    #     suppress[local['column']] = True
    #
    # for x in mapper['columns']:
    #     key = x['key']
    #     if key in suppress and suppress[key]:
    #         logger.debug("skipping suppressed column %s", key)
    #         continue
    #
    #     # vname = x.type.__visit_name__
    #     # if not vname in typemap:
    #     #     kind = typemap[''][0]
    #     # else:
    #     #     kind = typemap[vname][0]
    #
    #     kind = 'text'
    #     select_id = 'input_%s' % (key)
    #     f = {'input_name': prefix + key,
    #          'input_id': select_id,
    #          'input_value': ''}
    #
    #     input_html = render_template(request, "templates/entity/field\_%s.jinja2" % kind, f)
    #     #logger.debug("input_html = %s", input_html)
    #     e = {'id': select_id,
    #          'input_html': input_html,
    #          'label_html': label_html(request, select_id, stringcase.sentencecase(key)),
    #          'help': x['doc']
    #          }
    #     d['form_contents'] = d['form_contents'] + render_template(request, templates.field, e)
    #
    # outer_vars['readycode'] = readycode
    # return render_template(request, templates.form, d)


class BaseEntityRelatedView(BaseView):
    def __init__(self, context, request: Request = None) -> None:
        super().__init__(context, request)
        self._entity_type = None

    @property
    def entity_type(self):
        return self._entity_type

    @entity_type.setter
    def entity_type(self, new):
        self._entity_type = new


class EntityView(BaseEntityRelatedView):
    def __init__(self, context, request: Request = None) -> None:
        super().__init__(context, request)
        self._entity = None

    def query(self):
        return self.request.dbsession.query(self.entity_type)

    def load_entity(self):
        query = self.query()
        assert query is not None
        by = query.filter_by(id=self.id)
        assert by is not None
        self.entity = by.first()

    @property
    def entity(self):
        return self._entity

    @entity.setter
    def entity(self, new):
        self._entity = new

    @property
    def id(self):
        return self._values['id']

    @property
    def entity_type(self):
        return self._entity_type

    def __call__(self, *args, **kwargs):
        d = super().__call__(*args, **kwargs)
        request = self.request

        self.collect_args(request)

        self.load_entity()
        return {**d, 'entity': self.entity}


class EntityCollectionView(BaseEntityRelatedView):
    def __call__(self, *args, **kwargs):
        assert self.request is not None
        assert self._entity_type is not None
        collection = self.request.dbsession.query(self._entity_type).all()
        return {'entities': collection}


# TODO: this is clearly totally unimplememnted right now
@implementer(IEntryPointGenerator)
@adapter(IEntryPoint)
class FormViewEntryPointGenerator(EntryPointGenerator):
    def extra_js_stmts(self):
        return []

    def js_imports(self):
        return []

    def js_stmts(self):
        return []


@implementer(IFormContext)
@dataclass
class FormContext:
    env: IJinja2Environment
    request: Request = None
    mapper_info: MapperInfo = None
    outer_vars: dict = field(default_factory=lambda: {})
    nest_level: int = 0
    do_modal: bool = False
    prefix: str = ""
    form: Form = None
    extra: dict = field(default_factory=lambda: {'suppress_cols': {}})
    namespace: INamespaceStore = None


# class IRelationshipFormRenderer:
#     pass
#
# @adapter(IRelationshipInfo)
# @implementer(IRelationshipFormRenderer)
# class RelationshipFormRenderer:
#     def render_relationship_form(self):
#         pass


@implementer(IRelationshipSelect)
class RelationshipSelect:
    def __init__(self, info) -> None:
        super().__init__()
        self._rel_info = info
        self._context = None

    def set_context(self, context):
        self._context = context

    def get_select(self):
        context = self._context
        rel = self._rel_info
        request = context.request
        prefix = ''
        nest_level = context.nest_level

        argument = rel.argument
        pairs = rel.local_remote_pairs
        local = pairs[0].local
        remote = pairs[0].remote

        key_ = rel.key
        assert key_ is not None

        label_contents = stringcase.sentencecase(key_)

        select_id = context.form.get_html_id('id_select_%s' % key_)  # ['select', prefix, key_])

        select_name = "select_" + key_
        select_name = context.form.get_html_form_name(select_name, True)

        class_ = argument
        entities = []
        if issubclass(class_, Base):
            try:
                entities = request.dbsession.query(class_).all()
            except AttributeError as ex:
                pass

        modal_id = context.form.get_html_id('modal_%s%s' % (prefix, key_), True)
        buttons = []
        collapse = ''
        button_id = context.form.get_html_id('button_%s%s' % (prefix, key_), True)
        collapse_id = context.form.get_html_id('collapse_%s%s' % (prefix, key_), True)

        #            mappers_ = alchemy['mappers']
        # control excessive nesting
        if nest_level < 1:
            key = rel.key

            # this is bogus??
            mapper2 = request.registry.queryUtility(IMapperInfo, remote.table)

            prefix_key_ = "%s%s." % (prefix, key)
            logger.debug("prefix_key_ = %s", prefix_key_)
            sub_namespace = context.form.namespace.make_namespace(key)
            context2 = FormContext(context.env, context.request,
                                   mapper2.get_one_mapper_info(),
                                   context.outer_vars, context.nest_level + 1,
                                   context.do_modal,
                                   namespace=sub_namespace,
                                   extra=context.extra)

            builder = context.request.registry.getAdapter(context2, IFormRepresentationBuilder)
            entity_form = builder.form_representation()

            logger.debug("entity_form = %s", entity_form)

            button = FormButton('button',
                                {'id': button_id.get_id(),
                                 'class': 'btn btn-primary'})
            button.element.text = 'Create New'
            buttons.append(button)

        options = []
        for entity in entities:
            option = FormOptionElement(entity.display_name,
                                       entity.__dict__[remote.column])
            options.append(option)

        select = FormSelect(name=select_name.get_id(), id=select_id.get_id(), options=options,
                            attr={"class": "form-control"})
        select_name.set_element(select)
        select_id.set_element(select)
        label = FormLabel(form_control=select, label_contents=label_contents,
                          attr={"class": "col-sm-4 col-form-label"})

        rel_select = select.as_html()
        logger.debug("select = %s", rel_select, extra={'element': select})

        logger.debug("suppressing column %s", local.column)
        context.extra['suppress_cols'][local.column] = True

        _vars = {'input_html': rel_select,
                 'label_html': label.as_html(),
                 'collapse': collapse,
                 'help': rel.doc}

        env = request.registry.getUtility(IJinja2Environment, 'app_env')
        x = env.get_template('entity/field_relationship.jinja2').render(**_vars)

        # src = request.registry.getUtility(ITemplateSource, 'entity/field_relationship.jinja2')
        # tmp = request.registry.getAdapter(src, ITemplate)
        # x = tmp.render(**_vars)
        # logger.debug("result is %s", x)
        assert x
        return x


@adapter(IFormContext)
@implementer(IFormRepresentationBuilder)
class FormRepresentationBuilder:
    def __init__(self, context: IFormContext) -> None:
        self._context = context

    def form_representation(self):
        # having context passed in noew seems redundant
        context = self._context
        mapper = context.mapper_info
        assert context.prefix == ""
        prefix = context.prefix
        request = context.request

        outer_form = False
        if context.nest_level == 0:
            outer_form = True

        mapper_key = mapper.local_table.key
        namespace_id = mapper_key
        logger.debug("in form_representation with namespace id of %s", namespace_id)
        the_form = Form(request, namespace_id, context.namespace,  # can be None
                        outer_form=outer_form)
        context.form = the_form
        assert prefix is not None

        form_contents = '<div>'
        #        the_form.set_mapper_info(mapper.local_table.key, mapper)

        # we want a script tag containing stuff we like
        #         script = html.Element('script')
        # #        script.text = "mapper = %s;" % json.dumps(mapper)
        #         the_form.element.append(script)
        logger.info("Generating form representation for prefix=%s, %s" % (prefix, mapper_key))

        # suppress primary keys
        suppress = context.extra['suppress_cols'] = {}
        for akey in mapper.primary_key:
            assert akey.table == mapper.local_table.key
            suppress[akey.column] = True

        form_html = {}
        # PROCESS RELATIONSHIP
        # for each relationship
        # where its appropriate, embed or supply a subordinate form
        # additionally, supply a form variable and mapping for the relevant column.
        for rel in mapper.relationships:
            logger.debug("extra = %s", context.extra)
            rel_mapper = context.request.registry.getMultiAdapter((rel, context), IFormRelationshipMapper)
            form_html[rel.local_remote_pairs[0].local.column] = rel_mapper.map_relationship()
            logger.debug("now extra = %s", context.extra)

        # process each column
        for x in mapper.columns:
            key = x.key
            if key in form_html:
                form_contents = form_contents + form_html[key]
                continue

            if key in suppress and suppress[key]:
                logger.debug("skipping suppressed column %s", key)
                continue

            logger.debug("Mapping column %s", key)

            # FIXME we default to text because we're lazy
            kind = 'text'
            input_id = 'input_%s' % key
            input_id = context.form.get_html_id(input_id, True)
            input_name = prefix + key
            input_name = context.form.get_html_form_name(input_name, True)
            f = {'input_name': input_name,
                 'input_id': input_id,
                 'input_value': ''}

            div_col_sm_8 = DivElement('div', {'class': 'col-sm-8'})

            input_control = FormTextInputElement({'id': input_id.get_id(),
                                                  'value': '',
                                                  'name': input_name.get_id(),
                                                  'class': 'form-control'})
            div_col_sm_8.element.append(input_control.element)

            label_contents = stringcase.sentencecase(key)
            label = FormLabel(form_control=input_control, label_contents=label_contents,
                              attr={"class": "col-sm-4 col-form-label"})

            e = {'id': input_id,
                 'input_html': div_col_sm_8.as_html(),
                 'label_html': label.as_html(),
                 'help': x.doc,
                 }

            tmpl_name = 'entity/field.jinja2'
            x = context.env.get_template(tmpl_name).render(**e)
            #
            # src = request.registry.getUtility(ITemplateSource, tmpl_name)
            # tmp = request.registry.getAdapter(src, ITemplate)
            # x = tmp.render(**e)
            assert x

            logger.debug("got %s", x)
            form_contents = form_contents + x

        form_contents = form_contents + '</div>'
        the_form.element.append(html.fromstring(form_contents))

        return the_form


class EntityFormViewEntryPointGenerator(FormViewEntryPointGenerator):
    def __init__(self, entry_point: EntryPoint, request, **kwargs) -> None:
        super().__init__(entry_point, request, **kwargs)

    def generate(self):
        outer_vars = {}
        # we might want to query for a mapper? except our entry point has it
        # request.registry.queryUtility(IMapperInfo,

        request = self._request
        util = request.registry.getUtility
        adapt = request.registry.getAdapter
        multi = request.registry.getMultiAdapter

        env = util(IJinja2Environment, 'app_env')
        # for var in ('js_imports', 'js_stmts', 'extra_js_stmts'):
        #     v = TemplateVariable(var, [])
        #     c = adapt(v, ICollector)
        #     request.registry.registerUtility(c, ICollector, var)

        context = FormContext(env, request,
                              self.entry_point._mapper_wrapper.mapper_info,
                              # FIXME code smell digging into class internals
                              outer_vars,
                              )
        builder = context.request.registry.getAdapter(context, IFormRepresentationBuilder)
        logger.debug("calling builder.form_representation")
        self._form = builder.form_representation()

    def render_entity_form_wrapper(self, context: FormContext):
        form = self.render_entity_form(context)
        # FIXME still weird templating
        return render_template(context.request, templates.form_wrapper, {'form': form})

    def render_entity_form(self, context: FormContext):
        builder = context.request.registry.getAdapter(context, IFormRepresentationBuilder)
        self._form = builder.form_representation()
        return self._form.as_html()

    def js_stmts(self):
        utility = self._request.registry.queryUtility(ICollector, 'js_stmts')
        if utility:
            return utility.get_value()
        return []

    def extra_js_stmts(self):
        utility = self._request.registry.queryUtility(ICollector, 'extra_js_stmts')
        if utility:
            return utility.get_value()
        return []

    def js_imports(self):
        utility = self._request.registry.queryUtility(ICollector, 'js_imports')
        if utility:
            return utility.get_value()
        return []


class DesignViewEntryPointGenerator(EntryPointGenerator):
    def js_imports(self):
        return []  # "'../design.js'"]

    def js_stmts(self):
        return ['window.view_name = \'%s\';' % self._request.view_name]

    def extra_js_stmts(self):
        return []


class EntityDesignViewEntryPointGenerator(DesignViewEntryPointGenerator):
    pass


class EntityDesignView(BaseEntityRelatedView):
    pass


class EntityFormView(BaseEntityRelatedView):
    @staticmethod
    def entry_point_generator_factory():
        return EntityFormViewEntryPointGenerator

    def __init__(self, context, request: Request = None) -> None:
        super().__init__(context, request)

    def __call__(self, *args, **kwargs):
        generator = self.entry_point_generator_factory()(self.entry_point, self.request)
        mapper_info = self.entry_point.mapper_wrapper.get_one_mapper_info()
        if self.request.method == "GET":
            outer_vars = {}
            env = self._request.registry.getUtility(IJinja2Environment, 'app_env')
            context = FormContext(env, request=self.request,
                                  mapper_info=mapper_info,
                                  outer_vars=outer_vars)

            wrapper = generator.render_entity_form_wrapper(context)
            # FIXME still weird templating!
            # src = self._request.registry.getUtility(ITemplateSource, 'entity/form_enclosure.jinja2')
            # tmp = self._request.registry.getAdapter(src, ITemplate)
            _vars = {**outer_vars, 'entry_point_template':
                'build/templates/entry_point/%s.jinja2' % self.entry_point.key,
                     'form_content': wrapper}
            # x = tmp.render(**_vars)
            return Response(env.get_template('entity/form_enclosure.jinja2').render(**_vars))

        # this is for post!
        r = self.entity_type.__new__(self.entity_type)
        r.__init__()

        cols = list(self.inspect.columns)
        for col in cols:
            if col.key in self.request.params:
                v = self.request.params[col.key]
                if logger:
                    logger.info("%s = %s", col.key, v)
                r.__setattr__(col.key, v)

        self.request.dbsession.add(r)
        self.request.dbsession.flush()

        return Response("")


class EntityFormActionView(BaseEntityRelatedView):
    pass


class EntityAddView(BaseEntityRelatedView):
    pass


def includeme(config: Configurator):
    #    config.registry.registerUtility(RelationshipSelect, IRelationshipSelect)
    reg = config.registry.registerAdapter
    reg(RelationshipSelect, [IRelationshipInfo], IRelationshipSelect)
    reg(FormRepresentationBuilder, [IFormContext], IFormRepresentationBuilder)
    reg(FormRelationshipMapper, [IRelationshipInfo, IFormContext], IFormRelationshipMapper)
# reg(RelationshipFormRenderer, [IRelationshipInfo], IRelationshipFormRenderer)
