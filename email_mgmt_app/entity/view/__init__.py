from typing import TypeVar, Generic

from pyramid.request import Request


class BaseView(object):
    def __init__(self, context, request: Request=None) -> None:
        self._request = request

    def __call__(self, *args, **kwargs):
        return None

    @property
    def request(self) -> Request:
        return self._request


BaseEntityRelatedView_RelatedEntityType = TypeVar('BaseEntityRelatedView_RelatedEntityType')


class BaseEntityRelatedView(Generic[BaseEntityRelatedView_RelatedEntityType], BaseView):
    def __init__(self, context, request: Request = None) -> None:
        super().__init__(context, request)