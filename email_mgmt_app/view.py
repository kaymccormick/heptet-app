import logging
import sys

from pyramid.config import Configurator
from pyramid.interfaces import IRequestFactory
from pyramid.request import Request

from email_mgmt_app.argument import ArgumentContext
from email_mgmt_app.exceptions import MissingArgumentException, BaseAppException, OperationArgumentException
from email_mgmt_app.entrypoint import EntryPoint
from email_mgmt_app.util import get_exception_entry_point_key

logger = logging.getLogger(__name__)

class ViewConfig:
    pass


class BaseView:
    entry_point_generator = None
    def __init__(self, context, request: Request=None) -> None:
        self._context = context
        self._request = request
        self._operation = None
        self._values = {}
        self._response_dict = { 'request': request,
                                'context': context } # give it a nice default?
        self._entry_point_key = None
        #renderer = "templates/entity/%s.jinja2" % request.view_name.lower()
        #request.override_renderer = renderer

    def __call__(self, *args, **kwargs):
        self.collect_args(self.request)
        self._response_dict['entry_point_key'] = self.entry_point_key
        self._response_dict['entry_point_template'] = 'build/templates/entry_point/%s.jinja2' % self.entry_point_key

        return self._response_dict

    @property
    def request(self) -> Request:
        return self._request

    @request.setter
    def request(self, new: Request) -> None:
        self._request = new

    @property
    def operation(self) -> 'ResourceOperation':
        return self._operation

    @operation.setter
    def operation(self, new) -> None:
        self._operation = new

    @property
    def entry_point_key(self):
        return self._entry_point_key

    @entry_point_key.setter
    def entry_point_key(self, new):
        self._entry_point_key = new

    def collect_args(self, request):
        if self.operation is None:
            return
        assert self.operation is not None
        args = self.operation.args
#        logging.warning("checking args %s", repr(args))
        values = []
        arg_context = ArgumentContext()
        arg=None # type: 'OperationArgument'
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
                    raise MissingArgumentException(self.operation, arg, "Missing argument %s for operation %s" % (arg.name, self.operation.name))

            if not got_value:
                value = arg.get_value(request, arg_context)
                got_value = True

            self._values[arg.name] = value
            values.append(value)


class ExceptionView(BaseView):
    def __init__(self, context, request) -> None:
        super().__init__(context, request)
        #request.override_renderer = "templates/exception.jinja2"


class OperationArgumentExceptionView(ExceptionView):
    def __init__(self, context, request) -> None:
        super().__init__(context, request)
        request.override_renderer = "templates/args.jinja2"


def includeme(config: Configurator):
    def action():
        logger.info("Executing config action [exception views].")
        request = config.registry.queryUtility(IRequestFactory, default=Request)({})
        request.registry = config.registry

        entry_point_key = get_exception_entry_point_key(request, Exception)
        config.add_exception_view(view=ExceptionView, context=Exception,
                                  renderer="templates/exception/exception.jinja2",
                                  entry_point_key=entry_point_key)

        # need to issue more context!
        entry_point = EntryPoint(entry_point_key)
        config.register_entry_point(entry_point)


        config.add_exception_view(view=OperationArgumentExceptionView, context=OperationArgumentException,
                                  renderer="templates/exceptions/OperationArgumentException.jinja2",
                                  entry_point_key=entry_point_key)
        entry_point_key = get_exception_entry_point_key(request, OperationArgumentException)
        entry_point = EntryPoint(entry_point_key)
        config.register_entry_point(entry_point)
    config.action(None, action)
