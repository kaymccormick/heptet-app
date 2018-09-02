import json
import logging
from dataclasses import dataclass
from typing import TypeVar, Generic

import stringcase

from email_mgmt_app.form import *
from email_mgmt_app.entrypoint import *
from pyramid.interfaces import IRendererFactory
from pyramid.request import Request
from pyramid.response import Response
from sqlalchemy.orm.base import MANYTOONE

from email_mgmt_app.info import MapperInfo
from email_mgmt_app.adapter import AlchemyInfo
from email_mgmt_app.model.meta import Base
from email_mgmt_app.util import render_template
from pyramid.util import DottedNameResolver
from view import BaseView

logger = logging.getLogger(__name__)


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
    #     input_html = render_template(request, "templates/entity/field_%s.jinja2" % kind, f)
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


EntityView_EntityType = TypeVar('EntityView_EntityType', bound=Base)


class BaseEntityRelatedView(Generic[BaseEntityRelatedView_RelatedEntityType], BaseView):
    def __init__(self, context, request: Request = None) -> None:
        super().__init__(context, request)
        self._entity_type = request.context.resource_manager.entity_type

    @property
    def entity_type(self):
        return self._entity_type

    @entity_type.setter
    def entity_type(self, new):
        self._entity_type = new

    # @property
    # def inspect(self) -> Mapper:
    #     return self._inspect
    #
    # @inspect.setter
    # def inspect(self, new: Mapper):
    #     self._inspect = new


class EntityView(BaseEntityRelatedView[EntityView_EntityType]):
    def query(self):
        return self.request.dbsession.query(self.entity_type)

    def load_entity(self):
        query = self.query()
        assert query is not None
        by = query.filter_by(id=self.id)
        assert by is not None
        self.entity = by.first()

    @property
    def entity(self) -> EntityView_EntityType:
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


EntityCollectionView_EntityType = TypeVar('EntityCollectionView_EntityType')


class EntityCollectionView(BaseEntityRelatedView[EntityCollectionView_EntityType]):
    def __call__(self, *args, **kwargs):
        assert self.request is not None
        assert self._entity_type is not None
        collection = self.request.dbsession.query(self._entity_type).all()
        return {'entities': collection}


EntityFormView_EntityType = TypeVar('EntityFormView_EntityType')


class FormViewEntryPointGenerator(EntryPointGenerator):
    def extra_js_stmts(self):
        return []

    def js_imports(self):
        return []

    def js_stmts(self):
        return []


class EntityFormViewEntryPointGenerator(FormViewEntryPointGenerator):
    def __init__(self, entry_point: EntryPoint, request, **kwargs) -> None:
        super().__init__(entry_point, request, **kwargs)
        outer_vars = {}
        self._form = self.form_representation(self._request,
                                              self.get_mapper_info(
                                                  self.entry_point.operation.resource_manager.mapper_info[
                                                      'mapper_key']), outer_vars)

    def form_representation(self, request,
                            mapper: dict,
                            outer_vars,
                            nest_level: int = 0,
                            do_modal=False,
                            prefix=""):
        the_form = Form()

        # smell TODO - we can have multiple mappers
        mapper_key = mapper['mapper_key']
        the_form.set_mapper_info(mapper_key, mapper)

        script = html.Element('script')
        logger.critical("mapper is %s", repr(mapper))
        script.text = "mapper = %s;" % json.dumps(mapper)
        the_form.element.append(script)

        self.logger.info("Generating form representation for prefix=%s, %s" % (prefix, mapper_key))

        suppress = {}

        alchemy = request.registry.email_mgmt_app.alchemy # type: AlchemyInfo

        # store these or just skip?
        for (pkey_table, pkey_col) in mapper['primary_key']:
            assert pkey_table == mapper['mapped_table']

            suppress[pkey_col] = True

        ## PROCESS RELATIONSHIP
        # for each relationship
        # where its appropriate, embed or supply a subordinate
        # form
        # additionally, supply a form variable
        # and mapping for the relevant column.
        for rel in mapper['relationships']:
            if rel['direction'] == MANYTOONE:
                continue

            argument = rel['argument']
            pairs = rel['local_remote_pairs']
            local = pairs[0]['local']
            remote = pairs[0]['remote']

            key_ = rel['key']
            label_contents = stringcase.sentencecase(key_)

            # decide here what control to use ....
            #
            select_id = 'select_%s%s' % (prefix, key_)
            select_name = prefix + local['column']

            # generate a list of available
            # entities - eventually we will
            # wish to constrain the query some.
            resolver = DottedNameResolver()
            join = '.'.join(argument)

            class_ = resolver.resolve(join)
            if issubclass(class_, Base) and 'dbsession' in request.__dict__:
                entities = request.dbsession.query(class_).all()
            else:
                entities = []

            select_contents = ''

            modal_id = 'modal_%s%s' % (prefix, key_)
            buttons = []
            collapse = ''
            button_id = 'button_%s%s' % (prefix, key_)
            collapse_id = 'collapse_%s%s' % (prefix, key_)

            mappers_ = alchemy['mappers']
            # control excessive nesting
            if nest_level < 1:
                key = rel['key']

                entity_form = self.form_representation \
                    (request,
                     mappers_[remote['table']],
                     outer_vars,
                     nest_level + 1,
                     do_modal=do_modal,
                     prefix="%s%s." % (prefix, key),
                     )

                # we use label_contents for the title of our modal

                collapse = ''  # render_template(request, templates.collapse, {'collapse_contents': entity_form,
                #                                            'collapse_id': collapse_id})
                #
                # readycode = readycode + render_template(request, templates.button_create_new_click_js,
                #                                         { 'button_id': button_id,
                #                                           'collapse_id': collapse_id,
                #                                           'select_id': select_id })

                # <button id="{{ button_id }}" type="button" class="btn btn-primary">Create New</button>

                button = FormButton('button',
                                    {'id': button_id,
                                     'class': 'btn btn-primary'})
                button.element.text = 'Create New'
                buttons.append(button)

            options = []
            # <option value="{{ option_value|e }}">{{ option_contents|e }}</option>
            # select_contents = select_contents + \
            #                   render_template(request, templates.rel_select_option,
            #                                   {'option_value': 0,
            #                  'option_contents': "None"})

            # select_contents = select_contents + \
            #                   render_template(request, templates.rel_select_option,
            #                                   {'option_value': -1,
            #                  'option_contents': "New"})

            for entity in entities:
                option = FormOptionElement(entity.display_name, entity.__dict__[remote['column']])
                options.append(option)

            select = FormSelect(name=select_name, id=select_id, options=options)
            label = FormLabel(form_control=select, label_contents=label_contents)

            rel_select = select.as_html()
            self.logger.debug("select = %s", rel_select, extra={'element': select})

            # d['form_contents'] = d['form_contents'] + render_template(request, templates.field_relationship,
            #                                                           {'input_html': rel_select,
            #                                                          'label_html': label_html(request, select_id,
            #                                                                                   label_contents),
            #                                                          'collapse': collapse,
            #                                                          'help': rel['doc']})

            self.logger.debug("suppressing column %s", local['column'])
            suppress[local['column']] = True

        for x in mapper['columns']:
            key = x['key']
            if key in suppress and suppress[key]:
                self.logger.debug("skipping suppressed column %s", key)
                continue

            # vname = x.type.__visit_name__
            # if not vname in typemap:
            #     kind = typemap[''][0]
            # else:
            #     kind = typemap[vname][0]

            kind = 'text'
            select_id = 'input_%s' % (key)
            f = {'input_name': prefix + key,
                 'input_id': select_id,
                 'input_value': ''}

            # input_html = render_template(request, "templates/entity/field_%s.jinja2" % kind, f)
            # self.logger.info("input_html = %s", input_html)
            e = {'id': select_id,
                 'input_html': '',
                 'label_html': '',#label_html(request, select_id, stringcase.sentencecase(key)),
                 'help': x['doc']
                 }
        #        d['form_contents'] = d['form_contents'] + render_template(request, templates.field, e)

        # outer_vars['readycode'] = readycode
        return the_form

    def render_entity_form_wrapper(self, request, inspect, outer_vars, nest_level: int = 0, do_modal=False, prefix=""):
        form = self.render_entity_form(request, inspect, outer_vars, nest_level, do_modal, prefix)
        return render_template(request, templates.form_wrapper, {'form': form})

    def render_entity_form(self, request, mapper: MapperInfo, outer_vars, nest_level: int = 0, do_modal=False,
                           prefix=""):
        form = self.form_representation(request, mapper, outer_vars, nest_level, do_modal, prefix)
        return form.as_html()

    def js_stmts(self):
        return []

    def extra_js_stmts(self):
        return []

    def js_imports(self):
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
    entry_point_generator = EntityDesignViewEntryPointGenerator


class EntityFormView(BaseEntityRelatedView[EntityFormView_EntityType]):
    entry_point_generator = EntityFormViewEntryPointGenerator

    def __call__(self, *args, **kwargs):
        self.entry_point_generator()
        if self.request.method == "GET":
            outer_vars = {}
            wrapper = self.render_entity_form_wrapper(
                self.request,
                self.request.registry.email_mgmt_app.alchemy['mappers'] \
                    [self.mapper_info['mapper_key']],
                outer_vars)
            return Response(render_template(self.request, templates.form_enclosure,
                                            {**outer_vars, 'entry_point_template':
                                                'build/templates/entry_point/%s.jinja2' % self.entry_point_key,
                                             'form_content': wrapper}))

        # this is for post!
        r = self.entity_type.__new__(self.entity_type)
        r.__init__()

        cols = list(self.inspect.columns)
        for col in cols:
            if col.key in self.request.params:
                v = self.request.params[col.key]
                self.logger.info("%s = %s", col.key, v)
                r.__setattr__(col.key, v)

        self.request.dbsession.add(r)
        self.request.dbsession.flush()

        return Response("")


EntityFormActionView_EntityType = TypeVar('EntityFormActionView_EntityType')


class EntityFormActionView(BaseEntityRelatedView[EntityFormActionView_EntityType]):
    pass


EntityAddView_EntityType = TypeVar('EntityAddView_EntityType')


class EntityAddView(BaseEntityRelatedView[EntityAddView_EntityType]):
    pass


BaseEntityRelatedView_RelatedEntityType = TypeVar('BaseEntityRelatedView_RelatedEntityType')