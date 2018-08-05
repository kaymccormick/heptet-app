from typing import TypeVar

from pyramid.request import Request
from sqlalchemy.orm import Session

from email_mgmt_app.entity.model.meta import Base
from email_mgmt_app.entity.view import BaseEntityRelatedView

EntityView_EntityType = TypeVar('EntityView_EntityType', bound=Base)
class EntityView(BaseEntityRelatedView[EntityView_EntityType]):
    def __init__(self, request: Request = None, id: int=None) -> None:
        super().__init__(request)
        self._id = id
        self.load_entity()

    def load_entity(self):
        dbsession = self.request.dbsession # type: Session
        z = EntityView_EntityType # type: Base

        entity = dbsession.query(EntityView_EntityType).filter(id=id).first()

    @property
    def id(self):
        return self._id


EntityCollectionView_EntityType = TypeVar('EntityCollectionView_EntityType')
class EntityCollectionView(BaseEntityRelatedView[EntityCollectionView_EntityType]):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)