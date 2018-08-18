from typing import TypeVar, Generic

from pyramid.interfaces import IView
from pyramid.request import Request

from email_mgmt_app.util import munge_dict


class BaseView():
    def __init__(self, request: Request=None) -> None:
        self._request = request

    def __call__(self, *args, **kwargs):
        return munge_dict(self.request, {})

    @property
    def request(self) -> Request:
        return self._request


BaseEntityRelatedView_RelatedEntityType = TypeVar('BaseEntityRelatedView_RelatedEntityType')


class BaseEntityRelatedView(Generic[BaseEntityRelatedView_RelatedEntityType], BaseView):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)
        self._entity_type = request.context.registration.entity_type
