from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPClientError
from pyramid.interfaces import IExceptionResponse
from zope.interface import implementer



@implementer(IExceptionResponse)
class BaseAppException(HTTPClientError):
    pass

@implementer(IExceptionResponse)
class OperationException(BaseAppException):
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
