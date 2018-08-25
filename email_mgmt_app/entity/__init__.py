import logging
import sys
from typing import TypeVar

import stringcase
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.request import Request

from email_mgmt_app.entity.model.meta import Base
from email_mgmt_app.entity.view import BaseEntityRelatedView

from email_mgmt_app.util import munge_dict
from email_mgmt_app.exceptions import OperationArgumentException

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
        return munge_dict(self.request, { 'entity': self.entity })



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
    typemap = {'': ['text'] }



    def __init__(self, request: Request = None) -> None:
        super().__init__(request)

    def __call__(self, *args, **kwargs):
        d = super().__call__()
        from pyramid.renderers import get_renderer

        renderer1 = get_renderer("templates/entity/field.jinja2")
        loader = renderer1.template_loader()
        tmpl = loader
        logging.warning("tmpl= %s", tmpl)



        self.request.override_renderer = "templates/entity/form.jinja2"
        d['formcontents'] = ''
        for x in self.inspect.columns:
            vname = x.type.__visit_name__
            if not vname in self.typemap:
                kind = self.typemap[''][0]
            else:
                kind = self.typemap[vname][0]
            elem_id = 'input_%s' % (x.key)
            f = {'input_name': x.key,
                 'input_id': elem_id,
                 'input_value': ''}

            e = {'id': elem_id,
                 'input_html': get_renderer("templates/entity/field_%s.jinja2" % (kind)).template_loader().render(f),
                 'label_html': get_renderer("templates/entity/label.jinja2").template_loader().render({'for_id': elem_id, 'label': stringcase.sentencecase(x.key)})
            }
            d['formcontents'] = d['formcontents'] + tmpl.render(e)

        return d


EntityFormActionView_EntityType = TypeVar('EntityFormActionView_EntityType')


class EntityFormActionView(BaseEntityRelatedView[EntityFormActionView_EntityType]):
    def __call__(self, *args, **kwargs):
        return munge_dict(self.request, {})


EntityAddView_EntityType = TypeVar('EntityAddView_EntityType')


class EntityAddView(BaseEntityRelatedView[EntityAddView_EntityType]):
    pass

