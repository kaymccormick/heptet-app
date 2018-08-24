from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPBadRequest, HTTPClientError
from pyramid.interfaces import IExceptionResponse
from pyramid.response import Response
from pyramid.scaffolds import Template
from pyramid.view import view_config
from zope.interface import implementer

from email_mgmt_app.util import munge_dict

@implementer(IExceptionResponse)
class BaseException(HTTPClientError):
    pass

@implementer(IExceptionResponse)
class OperationException(BaseException):
    code = 500
    title = 'Operation Exception'
    explanation = 'Operation Exception'

    def __init__(self, operation):
        super().__init__()
        self.operation = operation

@implementer(IExceptionResponse)
class OperationArgumentException(OperationException):
    def __init__(self, operation, arg):
        super().__init__(operation)
        self.arg = arg

@implementer(IExceptionResponse)
class MissingArgumentException(OperationArgumentException):
    explanation = 'Missing Argument'

class OperationArgumentExceptionView:
    def __init__(self, context, request) -> None:
        super().__init__()
        self.request = request
        self.context = context
        request.override_renderer = "templates/args.jinja2"


    def __call__(self):
        return munge_dict(self.request, { 'exception': self.context })


class ExceptionView():
    def __init__(self, context, request) -> None:
        super().__init__()
        self.request = request
        self.context = context
        request.override_renderer = "templates/exception.jinja2"


    def __call__(self):
        return munge_dict(self.request, { 'exception': self.context })



def includeme(config: Configurator):
    config.add_exception_view(view=ExceptionView,context=BaseException)
    config.add_exception_view(view=OperationArgumentExceptionView,context=OperationArgumentException)


