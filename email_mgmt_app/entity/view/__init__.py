import logging
import sys
from typing import TypeVar, Generic

from pyramid.interfaces import IView
from pyramid.request import Request
from webob import exc

from email_mgmt_app.util import munge_dict
from email_mgmt_app.res import ResourceOperation, OperationArgument
from email_mgmt_app.exceptions import InvalidArgumentException


class BaseView():
    def __init__(self, request: Request=None) -> None:
        self._request = request
        self._operation = None

    def __call__(self, *args, **kwargs):
        self.check_args(self.request)
        return munge_dict(self.request, {})

    @property
    def request(self) -> Request:
        return self._request

    @property
    def operation(self) -> ResourceOperation:
        return self._operation

    @operation.setter
    def operation(self, new) -> None:
        self._operation = new

    def check_args(self, request):
        if self.operation is None:
            return
        assert self.operation is not None
        args = self.operation.args
        logging.debug("checking args %s", repr(args))
        arg: OperationArgument
        for arg in args:
            if arg.get_value is not None:
                value = arg.get_value(request)
            if arg.optional and arg._default is None:
                raise InvalidArgumentException()


BaseEntityRelatedView_RelatedEntityType = TypeVar('BaseEntityRelatedView_RelatedEntityType')


class BaseEntityRelatedView(Generic[BaseEntityRelatedView_RelatedEntityType], BaseView):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)
        self._entity_type = request.context.registration.entity_type

    @property
    def entity_type(self):
        return self._entity_type

    @entity_type.setter
    def entity_type(self, new):
        self._entity_type = new
