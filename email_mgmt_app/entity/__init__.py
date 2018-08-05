from typing import TypeVar

from pyramid.request import Request

from email_mgmt_app.entity.view import BaseEntityRelatedView

EntityView_EntityType = TypeVar('EntityView_EntityType')
class EntityView(BaseEntityRelatedView[EntityView_EntityType]):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)

EntityCollectionView_EntityType = TypeVar('EntityCollectionView_EntityType')
class EntityCollectionView(BaseEntityRelatedView[EntityCollectionView_EntityType]):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)