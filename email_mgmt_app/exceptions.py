from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPClientError
from pyramid.interfaces import IExceptionResponse
from zope.interface import implementer


@implementer(IExceptionResponse)
class BaseAppException(HTTPClientError):
    def __init__(self, message):
        super().__init__(detail=message,comment=message)
        self.message = message


@implementer(IExceptionResponse)
class OperationException(BaseAppException):
    code = 500
    title = 'Operation Exception'
    explanation = 'Operation Exception'

    def __init__(self, operation, message):
        super().__init__(message)
        self.operation = operation


@implementer(IExceptionResponse)
class OperationArgumentException(OperationException):
    def __init__(self, operation, arg, message):
        super().__init__(operation, message)
        self.arg = arg


@implementer(IExceptionResponse)
class MissingArgumentException(OperationArgumentException):
    explanation = 'Missing Argument'
