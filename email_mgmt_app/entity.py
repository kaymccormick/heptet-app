import json
import re
from dataclasses import dataclass, field

import stringcase
from db_dump.info import MapperInfo, IRelationshipInfo

from email_mgmt_app.entrypoint import *
from email_mgmt_app.form import *
from email_mgmt_app.model.meta import Base
from email_mgmt_app.view import BaseView
from pyramid.config import Configurator
from pyramid.interfaces import IRequest
from pyramid.request import Request
from pyramid.response import Response
from pyramid_jinja2 import IJinja2Environment
from zope.interface.registry import Components

GLOBAL_NAMESPACE = 'global'
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
        request = context.request

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
    def __init__(self, entry_point: EntryPoint, view, request) -> None:
        super().__init__(entry_point, view, request)
        self._form = None

    def js_imports(self):
        return []

    def js_stmts(self):
        return []


@implementer(IFormContext)
@dataclass
class FormContext:
    env: IJinja2Environment
    registry: Components = None
    mapper_info: MapperInfo = None
    nest_level: int = 0
    do_modal: bool = False
    form: Form = None
    extra: dict = field(default_factory=lambda: {'suppress_cols': {}})
    namespace: NamespaceStore = None
    root_namespace: NamespaceStore = None


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
        env = request.registry.getUtility(IJinja2Environment, 'app_env')
        nest_level = context.nest_level

        argument = rel.argument
        pairs = rel.local_remote_pairs
        assert len(pairs) == 1
        (local, remote) = pairs[0]

        key = rel.key
        assert key

        label_contents = stringcase.sentencecase(key)

        select_id = context.form.get_html_id(stringcase.camelcase('id_select_%s' % key))  # ['select', prefix, key])
        select_name = stringcase.camelcase("select_" + key)
        select_name = context.form.get_html_form_name(select_name, True)

        class_ = argument
        entities = []
        if issubclass(class_, Base):
            try:
                entities = request.dbsession.query(class_).all()
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
            mapper2 = request.registry.queryUtility(IMapperInfo, remote.table)

            sub_namespace = context.form.namespace.make_namespace(stringcase.camelcase(key))
            context2 = FormContext(context.env, context.registry,
                                   mapper2.get_one_mapper_info(),
                                   context.nest_level + 1,
                                   context.do_modal,
                                   namespace=sub_namespace,
                                   extra=context.extra)

            builder = context.request.registry.getAdapter(context2, IFormRepresentationBuilder)
            entity_form = builder.form_representation()

            collapse = env.get_template('entity/collapse.jinja2').render(
                collapse_id=collapse_id.get_id(),
                collapse_contents=entity_form.as_html()
            )

            ready_stmts = request.registry.queryUtility(ICollector, 'ready_stmts')
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


@adapter(IFormContext)
@implementer(IFormRepresentationBuilder)
class FormRepresentationBuilder:
    def __init__(self, context: FormContext) -> None:
        """
        Fixed by ZCA
        :type context: FormContext
        :param context: The object to be adapted.
        """
        self._context = context

    def form_representation(self):
        """
        Generate a logical representation of an entity form.
        :return:
        """
        context = self._context
        mapper = context.mapper_info

        outer_form = False
        if context.nest_level == 0:
            outer_form = True

        mapper_key = mapper.local_table.key  # ??
        namespace_id = stringcase.camelcase(mapper_key)
        logger.debug("in form_representation with namespace id of %s", namespace_id)
        the_form = Form(context.registry, namespace_id, context.root_namespace, context.namespace,  # can be None
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
            rel_mapper = context.request.registry.getMultiAdapter((rel, context), IFormRelationshipMapper)
            column_name = rel.local_remote_pairs[0].local.column
            form_html[column_name] = rel_mapper.map_relationship()

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
            x = context.env.get_template(tmpl_name).render(**e)
            assert x
            form_contents = form_contents + x

        form_contents = form_contents + '</div>'
        the_form.element.append(html.fromstring(form_contents))

        return the_form


@implementer(IEntryPointGenerator)
@adapter(IFormContext, IFormRepresentationBuilder, IEntryPoint, IEntryPointView, IRequest)
class EntityFormViewEntryPointGenerator(FormViewEntryPointGenerator):

    def __init__(self, form_context, builder, entry_point: EntryPoint, view, request) -> None:
        super().__init__(entry_point, view, request)
        self._builder = builder
        self._form_context = form_context


    def generate(self):
        vars_ = ('js_imports', 'js_stmts', 'ready_stmts')

        # I am not sure 'resetting is the proper terminology'
        # logger.debug("Resetting template variables %s", vars_)

        t_vars = self.entry_point.vars
        for var in vars_:
            t_vars[var] = []

        registry = self.request.registry
        context = self._form_context #FormContext(registry,
        #                       # FIXME code smell digging into class internals
        #                       self.entry_point._mapper_wrapper.mapper_info,
        #                       )
        builder = self._builder
        self._form = builder.form_representation()
        root_namespace = context.root_namespace

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
        builder = context.request.registry.getAdapter(context, IFormRepresentationBuilder)
        self._form = builder.form_representation()

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


@implementer(IEntryPointView)
class EntityFormView(BaseEntityRelatedView):
    def __init__(self, context, request: Request = None) -> None:
        super().__init__(context, request)

    def __call__(self, *args, **kwargs):
        context = self.context
        assert self.entry_point
        generator = self.entry_point.generator
        assert generator
        mapper_info = self.entry_point.mapper_wrapper.get_one_mapper_info()
        assert mapper_info
        if self.request.method == "GET":
            env = self._request.registry.getUtility(IJinja2Environment, 'app_env')
            context = FormContext(
                env, request=self.request,
                mapper_info=mapper_info,
            )

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
    reg(FormRepresentationBuilder, [IFormContext], IFormRepresentationBuilder)
    reg(FormRelationshipMapper, [IRelationshipInfo, IFormContext], IFormRelationshipMapper)
    reg(EntityFormViewEntryPointGenerator, [IEntryPoint, IEntryPointView], IEntryPointGenerator)
    # reg(EntityFormView, [IJinja2Environment, IEntryPoint, ],
    #    IEntryPointView)
