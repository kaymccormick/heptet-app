import logging

from pyramid.config import Configurator
from pyramid.interfaces import IRequestFactory
from pyramid.request import Request

from email_mgmt_app import ExceptionView, OperationArgumentExceptionView
from exceptions import OperationArgumentException
from entrypoint import EntryPoint
from util import get_exception_entry_point_key

logger = logging.getLogger(__name__)


def includeme(config: Configurator):
    def action():
        logger.info("Executing config action [exception views].")
        request = config.registry.queryUtility(IRequestFactory, default=Request)({})
        request.registry = config.registry

        entry_point_key = get_exception_entry_point_key(Exception)
        entry_point = EntryPoint(None, entry_point_key, request)
        # x = ExceptionView.entry_point_generator_factory()
        # generator = x(entry_point, request)
        # entry_point.generator = generator
        config.register_entry_point(entry_point)
        config.add_exception_view(view=ExceptionView, context=Exception,
                                  renderer="templates/exception/exception.jinja2",
                                  entry_point=entry_point)

        # need to issue more context!
        # entry point itself needs a way to 'declare' its dependencies

        entry_point_key = get_exception_entry_point_key(OperationArgumentException)
        entry_point = EntryPoint(None, entry_point_key, request)
        OperationArgumentException.entry_point = entry_point
        # generator = OperationArgumentExceptionView.entry_point_generator_factory()(entry_point, request)
        # entry_point.generator = generator
        config.register_entry_point(entry_point)
        config.add_exception_view(view=OperationArgumentExceptionView, context=OperationArgumentException,
                                  renderer="templates/exceptions/OperationArgumentException.jinja2",
                                  entry_point=entry_point)

    config.action(None, action)
