import logging

from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPNotFound

from heptet_app import ExceptionView, OperationArgumentExceptionView, EntryPoint
from heptet_app.exceptions import OperationArgumentException
from heptet_app.util import get_exception_entry_point_key

logger = logging.getLogger(__name__)


def app_exception_view(config, exception, view, renderer):
    entry_point_key = get_exception_entry_point_key(exception)
    # equivalent to using our factory but we'd probably ought to be consistent
    entry_point = EntryPoint(entry_point_key)
    config.register_entry_point(entry_point)
    config.add_exception_view(view=view, context=exception,
                              renderer=renderer,
                              entry_point=entry_point)


def includeme(config: Configurator):
    def action():
        logger.info("Executing config action [exception views].")
        config.app_exception_view(Exception, ExceptionView,
                                  "templates/exception/exception.jinja2")
        config.app_exception_view(OperationArgumentException, OperationArgumentExceptionView,
                                  "templates/exception/exception.jinja2")
        config.app_exception_view(HTTPNotFound, ExceptionView,
                                  "templates/exception/exception.jinja2")

    intr = config.introspectable('app modules', __name__, "App module %r" % __name__,
                                 'app modules')
    config.add_directive("app_exception_view", app_exception_view)
    disc = ('exception views',)
    config.action(None, action, introspectables=(intr,))

