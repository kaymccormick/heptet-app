import logging
import sys

from pyramid.config import Configurator
from pyramid.interfaces import IRequestFactory
from pyramid.request import Request

from email_mgmt_app import ArgumentContext
from exceptions import MissingArgumentException, BaseAppException, OperationArgumentException
from entrypoint import EntryPoint, EntryPointGenerator
from util import get_exception_entry_point_key
from res import Resource, OperationArgument

logger = logging.getLogger(__name__)


class ViewConfig:
    pass


class BaseView:
    def __init__(self, context, request: Request = None) -> None:
        self._context = context
        self._request = request
        self._operation = None
        self._values = {}
        self._entry_point = None
        self._response_dict = {'request': request,
                               'context': context}  # give it a nice default?
        self._template_env = None


    def __call__(self, *args, **kwargs):
        self.collect_args(self.request)
        assert self.entry_point
        self._response_dict['entry_point_key'] = self.entry_point.key
        assert self.entry_point, "Entry point for view should not be None"
        key = self.entry_point.key
        assert key, "Entry point key for view should be truthy"
        # todo it might be super helpful to sanity check this value, because this generates errors
        # later that t+race to here
        self._response_dict['entry_point_template'] = 'build/templates/entry_point/%s.jinja2' % key

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

    def collect_args(self, request):
        if self.operation is None:
            return
        assert self.operation is not None
        args = self.operation.args
        values = []
        arg_context = ArgumentContext()
        arg: 'OperationArgument' = None
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
                    raise MissingArgumentException(self.operation, arg, "Missing argument %s for operation %s" % (
                        arg.name, self.operation.name))

            if not got_value:
                value = arg.get_value(request, arg_context)
                got_value = True

            self._values[arg.name] = value
            values.append(value)

    @property
    def entry_point(self):
        return self._entry_point

    @property
    def context(self) -> Resource:
        return self._context


class ExceptionView(BaseView):
    def __init__(self, context, request) -> None:
        super().__init__(context, request)
        # request.override_renderer = "templates/exception.jinja2"


class OperationArgumentExceptionView(ExceptionView):
    def __init__(self, context, request) -> None:
        super().__init__(context, request)
        request.override_renderer = "templates/args.jinja2"


def includeme(config: Configurator):
    def action():
        logger.info("Executing config action [exception views].")
        request = config.registry.queryUtility(IRequestFactory, default=Request)({})
        request.registry = config.registry

        entry_point_key = get_exception_entry_point_key(Exception)
        entry_point = EntryPoint(entry_point_key, request)
        #x = ExceptionView.entry_point_generator_factory()
        #generator = x(entry_point, request)
        #entry_point.generator = generator
        config.register_entry_point(entry_point)
        config.add_exception_view(view=ExceptionView, context=Exception,
                                  renderer="templates/exception/exception.jinja2",
                                  entry_point=entry_point)

        # need to issue more context!
        # entry point itself needs a way to 'declare' its dependencies

        entry_point_key = get_exception_entry_point_key(OperationArgumentException)
        entry_point = EntryPoint(entry_point_key, request)
        #generator = OperationArgumentExceptionView.entry_point_generator_factory()(entry_point, request)
        #entry_point.generator = generator
        config.register_entry_point(entry_point)
        config.add_exception_view(view=OperationArgumentExceptionView, context=OperationArgumentException,
                                  renderer="templates/exceptions/OperationArgumentException.jinja2",
                                  entry_point=entry_point)

    config.action(None, action)
