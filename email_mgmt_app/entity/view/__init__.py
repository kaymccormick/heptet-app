import logging
import sys
from typing import TypeVar, Generic

from pyramid.request import Request

from email_mgmt_app.exceptions import MissingArgumentException
from email_mgmt_app.res import ResourceOperation, OperationArgument
from email_mgmt_app.util import munge_dict


class ArgumentContext:
    def __init__(self) -> None:
        self._subpath_index = 0

    @property
    def subpath_index(self):
        return self._subpath_index

    @subpath_index.setter
    def subpath_index(self, new):
        logging.info("setting subpath_index to %s", new)
        self._subpath_index = new


class BaseView():
    def __init__(self, request: Request=None) -> None:
        self._request = request
        self._operation = None
        self._values = {}

    def __call__(self, *args, **kwargs):
        self.collect_args(self.request)
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

    def collect_args(self, request):
        if self.operation is None:
            return
        assert self.operation is not None
        args = self.operation.args
        logging.debug("checking args %s", repr(args))
        values = []
        arg_context = ArgumentContext()
        arg: OperationArgument
        for arg in args:
            has_value = arg.has_value(request, arg_context)
            got_value = False
            value = None
            if has_value is None:
                try:
                    value = arg.get_value(request, arg_context)
                    got_value = True
                    has_value = value is not None
                except:
                    logging.info("ex: %s", sys.exc_info()[1])

            if not has_value:
                if arg._default is not None:
                    has_value = True
                    value = arg._default
                    got_value = True

            if not has_value:
                if not arg.optional:
                    raise MissingArgumentException(self.operation, arg)

            if not got_value:
                value = arg.get_value(request, arg_context)
                got_value = True

            self._values[arg.name] = value
            values.append(value)




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
