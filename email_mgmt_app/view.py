import logging

from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPNotFound

from email_mgmt_app import ExceptionView, OperationArgumentExceptionView
from email_mgmt_app.entrypoint import EntryPoint
from email_mgmt_app.exceptions import OperationArgumentException
from email_mgmt_app.util import get_exception_entry_point_key

logger = logging.getLogger(__name__)


def app_exception_view(config, exception, view, renderer):
    entry_point_key = get_exception_entry_point_key(exception)
    entry_point = EntryPoint(None, entry_point_key)
    config.register_entry_point(entry_point)
    config.add_exception_view(view=view, context=Exception,
                              renderer=renderer,
                              entry_point=entry_point)


def includeme(config: Configurator):
    def action():
        logger.info("Executing config action [exception views].")
        config.app_exception_view(exception=Exception, view=ExceptionView,
                                  renderer="templates/exception/exception.jinja2")
        config.app_exception_view(exception=OperationArgumentException, view=OperationArgumentExceptionView,
                                  renderer="templates/exception/exception.jinja2")
        config.app_exception_view(exception=HTTPNotFound, view=ExceptionView,
                                  renderer="templates/exception/exception.jinja2")

        intr = config.introspectable('app modules', __name__, "App module %r" % __name__,
                                     'app modules')
        config.add_directive("app_exception_view", app_exception_view)
        disc = ('exception views',)
        config.action(None, action, introspectables=intr)
