from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPClientError
from pyramid.interfaces import IExceptionResponse
from zope.interface import implementer


class IdTaken(Exception):
    def __init__(self, html_id, ids) -> None:
        self.message = "HTML id %s taken" % html_id


class InvalidMode(Exception):
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)


class NamespaceCollision(Exception):
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)


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
