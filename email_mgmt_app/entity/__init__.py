import logging
from typing import TypeVar

import sqlalchemy
import stringcase
from pyramid.renderers import get_renderer
from pyramid.request import Request
from pyramid.response import Response
from sqlalchemy.orm import RelationshipProperty, Mapper
from sqlalchemy.orm.base import MANYTOONE

from email_mgmt_app.entity.model.meta import Base
from email_mgmt_app.entity.view import BaseEntityRelatedView
from email_mgmt_app.util import munge_dict


def label_html(request, elem_id, label_content):
    return render_template(request, "templates/entity/label.jinja2",
                           {'for_id': elem_id, 'label': label_content})


typemap = {'': ['text']}
rel_select_option_jinja_ = "templates/entity/rel_select_option.jinja2"
renderers = {}


def render_template(request, template_name, d):
    if template_name in renderers:
        renderer = renderers[template_name]
    else:
        renderer = get_renderer(template_name).template_loader()
        renderers[template_name] = renderer
    return renderer.render(munge_dict(request, d))


def render_entity_form(request, inspect):
    logging.info("Rendering entity form for %s" % inspect.mapped_table)
    d = {'formcontents': '', 'header': stringcase.sentencecase(inspect.mapped_table.key),
         'header2': inspect.entity.__doc__ or '',
         'modals': ''}

    suppress = {}

    for pkey_col in inspect.primary_key:
        suppress[pkey_col.key] = True

    relationships = list(inspect.relationships)
    logging.info("interating over relationships: %s", repr(relationships))

    rel: RelationshipProperty
    for rel in relationships:
        arg = rel.argument
        logging.debug("rel.argument = %s", repr(arg))
        if rel.parent != inspect.mapper or rel.direction != MANYTOONE:
            continue
        if callable(arg):
            rel_o = arg()
            logging.debug("rel.argument is callable, got %s", repr(rel_o))
        elif isinstance(arg, Mapper):
            rel_o = arg.entity
            logging.debug("rel.argument is instance of mapper, entity is %s", repr(rel_o))

        label_contents = stringcase.sentencecase(rel.key)
        key = rel_o.__tablename__
        entities = request.dbsession.query(rel_o).all()
        select_contents = ''

        modal_id = 'modal_%s' % rel.key
        d['modals'] = d['modals'] + render_template \
            (request, 'templates/entity/modal.jinja2',
             {
                 'is_modal': True,
                 'modal_id': modal_id, 'modal_title': label_contents,
                 'modal_body': render_entity_form(request,
                                                  request.registry.email_mgmt_app.mappers[rel_o.__name__.lower()])
             }
             )

        for entity in entities:
            select_contents = select_contents + \
                              render_template(request, rel_select_option_jinja_,
                                              {'option_value': '',
                                               'option_contents': entity.display_name})
        elem_id = 'select_%s' % key
        rel_select = render_template(request, "templates/entity/rel_select.jinja2", {'select_name': key,
                                                                                     'select_id': elem_id,
                                                                                     'modal_id': modal_id,
                                                                                     'select_value': None,
                                                                                     'select_contents': select_contents})
        d['formcontents'] = d['formcontents'] + render_template(request, "templates/entity/field.jinja2",
                                                                {'input_html': rel_select,
                                                                 'label_html': label_html(request, elem_id,
                                                                                          label_contents

                                                                                          ),
                                                                 'help': rel.doc})

        for x in rel.local_columns:
            logging.critical("(%s) %s", rel_o, x.key)
            suppress[x.key] = True

    cols = list(inspect.columns)
    logging.debug("iterating over columns: %s", repr(cols))
    for x in inspect.columns:
        if x.key in suppress and suppress[x.key]:
            logging.debug("skipping suppressed column %s", x.key)
            continue

        vname = x.type.__visit_name__
        if not vname in typemap:
            kind = typemap[''][0]
        else:
            kind = typemap[vname][0]

        elem_id = 'input_%s' % (x.key)
        f = {'input_name': x.key,
             'input_id': elem_id,
             'input_value': ''}

        input_html = render_template(request, "templates/entity/field_%s.jinja2" % kind, f)
        logging.info("input_html = %s", input_html)
        e = {'id': elem_id,
             'input_html': input_html,
             'label_html': label_html(request, elem_id, stringcase.sentencecase(x.key)),
             'help': x.doc
             }
        d['formcontents'] = d['formcontents'] + render_template(request, "templates/entity/field.jinja2", e)

    return render_template(request, "templates/entity/form.jinja2", d)


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
        request = self.request

        self.collect_args(request)

        self.load_entity()
        return munge_dict(self.request, {'entity': self.entity})


EntityCollectionView_EntityType = TypeVar('EntityCollectionView_EntityType')


class EntityCollectionView(BaseEntityRelatedView[EntityCollectionView_EntityType]):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)

    def __call__(self, *args, **kwargs):
        assert self.request is not None
        assert self._entity_type is not None
        collection = self.request.dbsession.query(self._entity_type).all()
        return munge_dict(self.request, {'entities': collection})


EntityFormView_EntityType = TypeVar('EntityFormView_EntityType')


class EntityFormView(BaseEntityRelatedView[EntityFormView_EntityType]):

    def __init__(self, request: Request = None) -> None:
        super().__init__(request)
        self._renderers = {}

    def __call__(self, *args, **kwargs):
        entity_form_enclosure_jinja_ = "templates/entity/form_enclosure.jinja2"
        return Response(render_template(self.request, entity_form_enclosure_jinja_,
                                        {'form_content': render_entity_form(self.request, self.inspect)}))


EntityFormActionView_EntityType = TypeVar('EntityFormActionView_EntityType')


class EntityFormActionView(BaseEntityRelatedView[EntityFormActionView_EntityType]):
    def __call__(self, *args, **kwargs):
        return munge_dict(self.request, {})


EntityAddView_EntityType = TypeVar('EntityAddView_EntityType')


class EntityAddView(BaseEntityRelatedView[EntityAddView_EntityType]):
    pass
