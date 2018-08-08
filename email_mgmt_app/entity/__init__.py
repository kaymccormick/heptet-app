from typing import TypeVar

from pyramid.request import Request
from sqlalchemy.orm import Session

from email_mgmt_app.entity.model.meta import Base
from email_mgmt_app.entity.view import BaseEntityRelatedView


EntityView_EntityType = TypeVar('EntityView_EntityType', bound=Base)
class EntityView(BaseEntityRelatedView[EntityView_EntityType]):
    def __init__(self, context, request: Request = None, id: int=None) -> None:
        super().__init__(context, request)
        self._entity_type = None
        self._id = id

    def query(self):
        return self.request.dbsession.query(self.entity_type)

    def load_entity(self):
        query = self.query()
        assert query is not None
        by = query.filter_by(id=self.id)
        assert by is not None
        entity = by.first()

    @property
    def id(self):
        return self._id

    @property
    def entity_type(self):
        return self._entity_type

EntityCollectionView_EntityType = TypeVar('EntityCollectionView_EntityType')
class EntityCollectionView(BaseEntityRelatedView[EntityCollectionView_EntityType]):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)