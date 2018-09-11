import json
import re
from typing import Mapping

import stringcase
from pyramid.request import Request
from pyramid.response import Response
from sqlalchemy.ext.declarative import DeclarativeMeta

from context import ContextFormContextMixin, EntityTypeMixin
from db_dump.info import IRelationshipInfo
from entrypoint import *
from form import *
from interfaces import IFormContext
from model import get_column_map
from model.meta import Base
from view import BaseView

GLOBAL_NAMESPACE = 'global'
logger = logging.getLogger(__name__)


def _make_form_representation(context: FormContext):
    """
    Generate a logical representation of an entity form.
    :return:
    """

    assert context.relationship_field_mapper, "Need dependency relationship field mapper (%s)." % context.relationship_field_mapper
    mapper = context.generator_context.mapper_info

    outer_form = False
    if context.nest_level == 0:
        outer_form = True

    mapper_key = mapper.local_table.key  # ??
    namespace_id = stringcase.camelcase(mapper_key)
    logger.debug("in form_representation with namespace id of %s", namespace_id)
    # we should provide for initialize the form in another fashion for testability!!!
    the_form = Form(namespace_id=namespace_id,
                    root_namespace=context.root_namespace,
                    namespace=context.namespace,  # can be None
                    outer_form=outer_form)
    context.form = the_form

    form_contents = '<div>'
    #        the_form.set_mapper_info(mapper.local_table.key, mapper)

    # we want a script tag containing stuff we like
    #         script = html.Element('script')
    # #        script.text = "mapper = %s;" % json.dumps(mapper)
    #         the_form.element.append(script)
    logger.debug("Generating form representation for %s" % mapper_key)

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
        # rel_mapper = context.request.registry.getMultiAdapter((rel, context), IFormRe#lationshipMapper)

        # we specify relationship select here. However, there are other ways we'll wish to
        # render

        (local, remote) = rel.local_remote_pairs[0]
        column_name = local.column
        context.current_element = rel

        x = get_column_map(local)
        # store the html!
        form_html[column_name] = context.relationship_field_mapper(context,
                                                                   RelationshipSelect(context)).map_relationship()

    # process each column
    for x in mapper.columns:
        key = x.key
        if key in form_html:
            # we already have the html, append it and continue
            form_contents = form_contents + form_html[key]
            continue

        if key in suppress and suppress[key]:
            logger.debug("skipping suppressed column %s", key)
            continue

        logger.debug("Mapping column %s", key)

        # FIXME we default to text because we're lazy
        kind = 'text'
        camel_key = stringcase.camelcase("input_%s" % key).replace('_', '')
        # FIXME figure this out ?not much of a key with the replacements.
        assert '_' not in camel_key, "Bad key %s" % camel_key
        input_id = context.form.get_html_id(camel_key, True)
        input_name = stringcase.camelcase(key).replace('_', '')
        input_name = context.form.get_html_form_name(input_name, True)

        div_col_sm_8 = DivElement('div', {'class': 'col-sm-8'})

        input_control = FormTextInputElement({'id': input_id.get_id(),
                                              'value': '',
                                              'name': input_name.get_id(),
                                              'class': 'form-control'})
        input_id.element = input_control
        input_name.element = input_control
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
        x = context.template_env.get_template(tmpl_name).render(**e)
        assert x
        form_contents = form_contents + x

    form_contents = form_contents + '</div>'
    the_form.element.append(html.fromstring(form_contents))

    return the_form


class EntityFormRepresentation:
    pass


class EntityFormConfiguration(EntityTypeMixin[DeclarativeMeta]):
    def __init__(self, entity_type: DeclarativeMeta, field_renderers: Mapping[AnyStr, object]) -> None:
        super().__init__()
        self.entity_type = entity_type
        self.field_renderers = field_renderers

    def __repr__(self):
        return "EntityFormConfiguration(%s, field_renderers=%s)" % (
            repr(self.entity_type), repr(self.field_renderers))


class IFormFieldMapper(Interface):
    pass


class IFormRelationshipFieldMapper(IFormFieldMapper):
    pass


# contemplate this ... what does this class fundamentally do
# it maps a relationship field to the form HTML (currently only in 'new') mode
# in fact, this generates some js vars also. its really just a ridiculous wrapper around
# "gen_select_html"

@adapter(IFormContext)
@implementer(IFormRelationshipFieldMapper)
class FormRelationshipMapper:
    def __init__(self, context: FormContext, form_select, *args, **kwargs) -> None:
        self._context = context
        self._select = form_select

    def map_relationship(self):
        context = self._context
        rel = context.current_element
        assert rel is not None

        vars = context.generator_context.template_vars
        assert 'js_stmts' in vars
        js_stmts_col = vars['js_stmts']
        js_stmts_col.append('// %s' % rel)

        logger.debug("Encountering relationship %s", rel)
        assert rel.direction
        if rel.direction.upper() != 'MANYTOONE':
            return ""

        logger.debug("Processing relationship %s", rel)

        #
        # decide here what control to use . right now we default to select.
        #
        select = self._select
        select.context = context
        select_html = select.gen_select_html()
        assert select_html
        return select_html


class BaseEntityRelatedView(BaseView):
    def __init__(self, context, request: Request = None) -> None:
        super().__init__(context, request)
        self._entity_type = None
        self._entity = None

    @property
    def entity_type(self):
        return self._entity_type

    @entity_type.setter
    def entity_type(self, new):
        self._entity_type = new

    @property
    def entity(self):
        return self._entity

    @entity.setter
    def entity(self, new):
        self._entity = new


class EntityView(BaseEntityRelatedView):
    def __init__(self, context, request: Request = None) -> None:
        super().__init__(context, request)

    def query(self):
        return self.request.dbsession.query(self.entity_type)

    def load_entity(self):
        query = self.query()
        assert query is not None
        by = query.filter_by(id=self.id)
        assert by is not None
        self.entity = by.first()

    @property
    def id(self):
        return self._values['id']

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


class FormViewEntryPointGenerator(EntryPointGenerator):
    pass


class _template:
    __slots__ = ['name']

    def __init__(self, name) -> None:
        super().__init__()
        self.name = name


class _templates:
    __slots__ = ['collapse']

    def __init__(self) -> None:
        super().__init__()
        self.collapse = _template('entity/collapse.jinja2')


template = _templates()


# we should seaprate concernts here
# if we need to build the form representation, we should be able to do it before
# this point.
@adapter(IFormContext)
@implementer(IRelationshipSelect)
class RelationshipSelect:
    # we need something called a "builder" here
    def __init__(self, context: FormContext) -> None:
        super().__init__()
        self._context = context

    def gen_select_html(self):
        context = self._context
        rel = context.current_element
        env = context.template_env
        nest_level = context.nest_level

        argument = rel.argument
        pairs = rel.local_remote_pairs
        assert len(pairs) == 1
        (local, remote) = pairs[0]

        key = rel.key
        assert key

        label_contents = stringcase.sentencecase(key)

        assert context.form
        select_id = context.form.get_html_id(stringcase.camelcase('id_select_%s' % key))  # ['select', prefix, key])
        select_name = stringcase.camelcase("select_" + key)
        select_name = context.form.get_html_form_name(select_name, True)

        class_ = argument
        entities = []
        if issubclass(class_, Base):
            try:
                entities = context.dbsession.query(class_).all()
            except AttributeError as ex:
                pass

        modal_id = context.form.get_html_id(stringcase.camelcase('modal_%s' % key), True)
        buttons = []
        collapse = ''
        button_id = context.form.get_html_id(stringcase.camelcase('button_%s' % key), True)
        collapse_id = context.form.get_html_id(stringcase.camelcase('collapse_%s' % key), True)

        # control excessive nesting
        if nest_level < 1:
            # this is bogus??
            # mapper2 = request.registry.queryUtility(IMapperInfo, remote.table)

            sub_namespace = context.form.namespace.make_namespace(stringcase.camelcase(key))
            context2 = context.copy(nest=True)
            context2.namespace = sub_namespace

            entity_form = _make_form_representation(context2)

            collapse = env.get_template(template.collapse.name).render(
                collapse_id=collapse_id.get_id(),
                collapse_contents=entity_form.as_html()
            )


            ready_stmts = None#request.registry.queryUtility(ICollector, 'ready_stmts')
            if ready_stmts:
                ready_stmts.add_value(env.get_template('entity/button_create_new_js.jinja2').render(
                    button_id=button_id.get_id(),
                    collapse_id=collapse_id.get_id(),
                    select_id=select_id.get_id()
                ))

            button = FormButton('button',
                                {'id': button_id.get_id(),
                                 'class': 'btn btn-primary'})
            button.element.text = 'Create New'
            buttons.append(button.as_html())

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

        select_html = select.as_html()
        rel_select = env.get_template('entity/rel_select.jinja2').render(
            select_html=select_html,
            buttons="\n".join(buttons)
        )

        logger.debug("suppressing column %s", local.column)
        context.extra['suppress_cols'][local.column] = True

        _vars = {'input_html': rel_select,
                 'label_html': label.as_html(),
                 'collapse': collapse,
                 'help': rel.doc}

        x = env.get_template('entity/field_relationship.jinja2').render(**_vars)
        assert x
        return x


@implementer(IEntryPointGenerator)
@adapter(IGeneratorContext)
class EntityFormViewEntryPointGenerator(FormViewEntryPointGenerator, ContextFormContextMixin):

    def __init__(self, ctx: GeneratorContext) -> None:
        super().__init__(ctx)
        try:
            self.form_context = ctx.form_context(relationship_field_mapper=FormRelationshipMapper)
        except AssertionError as ex:
            logger.critical("Unable to create form context")
            logger.critical(ex)
            raise ex

    def form_representation(self):
        return _make_form_representation(self.form_context)

    def generate(self):
        vars_ = ('js_imports', 'js_stmts', 'ready_stmts')
        ctx = self.ctx
        t_vars = ctx.template_vars

        for var in vars_:
            t_vars[var] = []

        ctx = self.ctx
        if ctx.mapper_info is None:
            # fixme - we get called here when we shouldn't and our fix is to bail out right now
            logger.critical("no mapper! probably not gonna work.")
            return

        self._form = self.form_representation()

        root_namespace = ctx.root_namespace

        def get_data(ns):
            d_data = ns.get_namespace_data()
            r = {}
            for k, d_v in d_data.items():
                r[k] = get_data(d_v)
            return r

        data = get_data(root_namespace)
        # this is super random and generic.
        x = t_vars['js_stmts']
        s = json.dumps(data)
        r1 = r'([\'\\])'
        r2 = r'\\\1'
        y = re.sub(r1, r2, s)
        s_y = "const ns = JSON.parse('%s');" % y
        logger.debug("adding %s to %s", s_y, x)

        x.append(s_y)

    def render_entity_form_wrapper(self, context: FormContext):
        form = self.render_entity_form(context)
        return context.env.get_template('entity/form_wrapper.jinja2').render(
            form=form
        )

    def render_entity_form(self, context: FormContext):
        self._form = self.form_representation()

        return self._form.as_html()

    def js_stmts(self):
        utility = self._request.registry.queryUtility(ICollector, 'js_stmts')
        if utility:
            return utility.get_value()
        return []

    def js_imports(self):
        utility = self._request.registry.queryUtility(ICollector, 'js_imports')
        if utility:
            return utility.get_value()
        return []

    def ready_stmts(self):
        utility = self._request.registry.queryUtility(ICollector, 'ready_stmts')
        assert utility
        if utility:
            return utility.get_value()
        return []


class DesignViewEntryPointGenerator(EntryPointGenerator):
    def js_imports(self):
        return []  # "'../design.js'"]

    def js_stmts(self):
        return ['window.view_name = \'%s\';' % self._request.view_name]


class EntityDesignViewEntryPointGenerator(DesignViewEntryPointGenerator):
    pass


class EntityDesignView(BaseEntityRelatedView):
    pass


# class needs: entry point.
# we were passing entry point as argument to the view
# we have no control over the view being instantiated.
@implementer(IEntryPointView)
class EntityFormView(BaseEntityRelatedView):
    def __init__(self, context, request: Request = None) -> None:
        super().__init__(context, request)

    def __call__(self, *args, **kwargs):
        resource = self.context
        entry_point = resource.manager.entry_point
        assert entry_point
        generator = entry_point.generator
        assert generator
        mapper_info = entry_point.mapper_wrapper.get_one_mapper_info()
        assert mapper_info
        if self.request.method == "GET":
            env = resource.template_env
            namespace = resource.root_namespace
            if callable(namespace):
                namespace = namespace()

            # we shouldn't need to crate this

            wrapper = generator.render_entity_form_wrapper(context)
            _vars = {
                'entry_point_template':
                    'build/templates/entry_point/%s.jinja2' % self.entry_point.key,
                'form_content': wrapper,
            }
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
    reg = config.registry.registerAdapter
    reg(RelationshipSelect, [IRelationshipInfo], IRelationshipSelect)
    reg(FormRelationshipMapper, [IRelationshipInfo, IFormContext], IFormRelationshipFieldMapper)
    reg(EntityFormViewEntryPointGenerator, [IGeneratorContext], IEntryPointGenerator)
    # reg(EntityFormView, [IJinja2Environment, IEntryPoint, ],
    ##    IEntryPointView)
    pass
