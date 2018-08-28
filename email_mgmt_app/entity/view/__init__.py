from typing import TypeVar, Generic

from pyramid.request import Request
from sqlalchemy.orm import Mapper

from email_mgmt_app.view import BaseView

BaseEntityRelatedView_RelatedEntityType = TypeVar('BaseEntityRelatedView_RelatedEntityType')


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