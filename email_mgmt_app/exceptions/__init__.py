from pyramid.config import Configurator
from pyramid.interfaces import IExceptionResponse
from pyramid.response import Response
from pyramid.scaffolds import Template
from zope.interface import implementer


@implementer(IExceptionResponse)
class InvalidArgumentException(Response, Exception):
    body_template_obj = Template('''\
    ${explanation}${br}${br}
    ${detail}
    ${html_comment}
    ''')


class ExceptionView():

    def __init__(self, request) -> None:
        super().__init__()

    def __call__(self):
        return {}



def includeme(config: Configurator):
    config.add_exception_view(view=ExceptionView,context=InvalidArgumentException)