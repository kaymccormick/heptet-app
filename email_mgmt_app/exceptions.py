from string import Template

from pyramid.httpexceptions import HTTPServerError
from pyramid.interfaces import IExceptionResponse
from zope.interface import implementer


class InvalidMode(Exception):
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)


class NamespaceKeyException(Exception):
    pass


class InvalidNamespaceId(NamespaceKeyException):
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)


class NamespaceCollision(NamespaceKeyException):
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)


@implementer(IExceptionResponse)
class AppException(HTTPServerError):
    html_template_obj = Template('''\
<html>
 <head>
  <title>${status}</title>
 </head>
 <body>
  <h1>${status}</h1>
  ${body}
 </body>
</html>''')

    def __init__(self, message, wrapped=None):
        super().__init__(detail=message, comment=message)
        self.message = message


@implementer(IExceptionResponse)
class OperationException(AppException):
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
