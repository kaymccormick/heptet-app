import logging
from dataclasses import dataclass
from typing import TypeVar

import stringcase
from pyramid.interfaces import IRendererFactory
from pyramid.request import Request
from pyramid.response import Response
from sqlalchemy import Column
from sqlalchemy.orm import RelationshipProperty, Mapper
from sqlalchemy.orm.base import MANYTOONE

from email_mgmt_app.info import MapperInfo
from email_mgmt_app.adapter import AlchemyInfo
from email_mgmt_app.entity.model.meta import Base
from email_mgmt_app.entity.view import BaseEntityRelatedView
from email_mgmt_app.util import munge_dict
from email_mgmt_app.util import render_template


@dataclass
class Templates:
    label:              str = "templates/entity/label.jinja2"
    rel_select_option:  str = "templates/entity/rel_select_option.jinja2"
    rel_select:         str = "templates/entity/rel_select.jinja2"
    modal:              str = 'templates/entity/modal.jinja2'
    field:              str = "templates/entity/field.jinja2"
    field_relationship: str = "templates/entity/field_relationship.jinja2"
    form:               str = "templates/entity/form.jinja2"
    form_enclosure:     str = "templates/entity/form_enclosure.jinja2"
    form_wrapper:       str = "templates/entity/form_wrapper.jinja2"
    button_create_new:  str = "templates/entity/button_create_new.jinja2"
    button_create_new_click_js:  str = "templates/entity/button_create_new_js.jinja2"
    collapse:           str = "templates/entity/collapse.jinja2"


templates = Templates()


def label_html(request, elem_id, label_content):
    return render_template(request, templates.label,
                           {'for_id': elem_id, 'label': label_content})


typemap = {'': ['text']}
renderers = {}

def template_source(request, template_name):
    f = request.registry.queryUtility(IRendererFactory, '.jinja2')
    source = f.environment.loader.get_source({}, template_name)
    return source[0]


def render_entity_form_wrapper(request, inspect, outer_vars, nest_level: int=0,do_modal=False,prefix=""):
    form = render_entity_form(request, inspect, outer_vars, nest_level, do_modal, prefix)
    return render_template(request, templates.form_wrapper, {'form': form})


def render_entity_form(request, mapper: MapperInfo, outer_vars, nest_level: int=0,do_modal=False,prefix=""):
    mapped_table = "poop"
    logging.info("Rendering entity form for %s" % mapped_table)
    d = {'form_contents': '', 'header': stringcase.sentencecase(mapped_table),
         'header2': mapper['doc'] or '',
         'modals': ''}

    suppress = {}

    alchemy: AlchemyInfo
    alchemy = request.registry.email_mgmt_app.alchemy

    assert mapper

    # for pkey_col in inspect.primary_key:
    #     suppress[pkey_col.key] = True

    readycode = ''

    for rel in mapper['relationships']:
        if rel['direction'] == MANYTOONE:
            continue
        arg = rel['argument']
        rel_o = arg

        pairs = rel['local_remote_pairs']
        local = pairs[0]['local']
        remote = pairs[0]['remote']

        key_ = rel['key']
        label_contents = stringcase.sentencecase(key_)
        if isinstance(rel_o, Base):
            entities = request.dbsession.query(rel_o).all()
        else:
            entities = []

        select_contents = ''

        modal_id = 'modal_%s%s' % (prefix, key_)
        buttons = ''
        collapse = ''
        select_id = 'select_%s%s' % (prefix, key_)
        button_id = 'button_%s%s' % (prefix, key_)

        if nest_level < 1:
            logging.warning("keys = %s", repr(request.registry.email_mgmt_app.mappers.keys()))
            do_modal = False

            key = rel['key']
            entity_form = render_entity_form\
                ( request                           ,
                  alchemy.mappers[remote['table']]     ,
                  outer_vars                        ,
                  nest_level + 1                    ,
                  do_modal=do_modal                 ,
                  prefix="%s%s." % (prefix, key),
                  )

            if do_modal:
                d['modals'] = d['modals'] + render_template \
                    (request, templates.modal,
                     {
                         'is_modal': True,
                         'modal_id': modal_id, 'modal_title': label_contents,
                         'modal_body': entity_form
                     })
                # buttons = buttons + render_template(request, templates.button_create_new_modal, { 'modal_id': modal_id })
            else:
                collapse_id = 'collapse_%s' % key
                collapse = render_template(request, templates.collapse, {'collapse_contents': entity_form,
                                                                         'collapse_id': collapse_id})

                readycode = readycode + render_template(request, templates.button_create_new_click_js,
                                                        { 'button_id': button_id,
                                                          'collapse_id': collapse_id,
                                                          'select_id': select_id })

                buttons = buttons + render_template \
                    (request,
                     templates.button_create_new,
                     {'button_id': button_id,
                      'select_id': select_id,
                      'collapse_id': collapse_id})



        select_contents = select_contents + \
                          render_template(request, templates.rel_select_option,
                                          {'option_value': 0,
                         'option_contents': "None"})
        select_contents = select_contents + \
                          render_template(request, templates.rel_select_option,
                                          {'option_value': -1,
                         'option_contents': "New"})

        for entity in entities:
            select_contents = select_contents + \
                              render_template(request, templates.rel_select_option,
                                              {'option_value': entity.__dict__[remote.name],
                                               'option_contents': entity.display_name})


        rel_select = render_template(request, templates.rel_select, {'select_name': prefix + local['column'],
                                                                     'select_id': select_id,
                                                                     'select_value': None,
                                                                     'select_contents': select_contents,
                                                                     'buttons': buttons,

                                                                     'collapse': collapse,
                                                                     })
        d['form_contents'] = d['form_contents'] + render_template(request, templates.field_relationship,
                                                                  {'input_html': rel_select,
                                                                 'label_html': label_html(request, select_id,
                                                                                          label_contents),
                                                                 'collapse': collapse,
                                                                 'help': rel['doc']})

        suppress[local['column']] = True

    for x in mapper['columns']:
        key = x['key']
        if key in suppress and suppress[key]:
            logging.debug("skipping suppressed column %s", key)
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

        input_html = render_template(request, "templates/entity/field_%s.jinja2" % kind, f)
        logging.info("input_html = %s", input_html)
        e = {'id': select_id,
             'input_html': input_html,
             'label_html': label_html(request, select_id, stringcase.sentencecase(key)),
             'help': x['doc']
             }
        d['form_contents'] = d['form_contents'] + render_template(request, templates.field, e)

    outer_vars['readycode'] = readycode
    return render_template(request, templates.form, d)


EntityView_EntityType = TypeVar('EntityView_EntityType', bound=Base)


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
        return munge_dict(self.request, {'entities': collection})


EntityFormView_EntityType = TypeVar('EntityFormView_EntityType')


class EntityFormView(BaseEntityRelatedView[EntityFormView_EntityType]):
    def __call__(self, *args, **kwargs):
        if self.request.method == "GET":
            outer_vars = {}
            wrapper = render_entity_form_wrapper(
                self.request,
                self.request.registry.email_mgmt_app.alchemy.mappers\
                    [self.inspect.mapped_table.key],
                outer_vars)
            return Response(render_template(self.request, templates.form_enclosure,
                                            {**outer_vars, 'entry_point_template':
                                                'build/templates/entry_point/%s.jinja2' % self.entry_point_key,
                                                'form_content': wrapper}))

        #this is for post!
        r = self.entity_type.__new__(self.entity_type)
        r.__init__()

        cols = list(self.inspect.columns)
        for col in cols:
            if col.key in self.request.params:
                v = self.request.params[col.key]
                logging.info("%s = %s", col.key, v)
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
