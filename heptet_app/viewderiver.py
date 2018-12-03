import logging
import sys

from jinja2 import TemplateNotFound
from pyramid.httpexceptions import HTTPException
from pyramid.tweens import INGRESS

from heptet_app import BaseView

logger = logging.getLogger(__name__)


# this function needs major help! TODO
# i feel like we can replace this stuff with Contextfound stuff
def entity_view(view, info):
    # pull entity type from options (out of date!!)
    operation = info.options.get('operation')
    logger.critical("I am wrapping now! %r", info.original_view)

    def wrapper_view(context, request):
        logger.warning("original view = %s", repr(info.original_view))
        original_view = info.original_view

        # renderer = None
        if isinstance(original_view, type):
            if issubclass(original_view, BaseView):
                original_view.operation = operation
                original_view.entry_point = info.options['entry_point']

            # if issubclass(original_view, BaseEntityRelatedView):
            #     # is this still in effect? (why wouldn't it be in effect?)
            #     logger.debug("setting entity_type to %s (orig = %s)", et, str(original_view.entity_type))
            #     original_view.entity_type = et
            #     original_view.mapper_info = mapper_info

        # if renderer:

        #     request.override_renderer = renderer

        response = view(context, request)
        return response

    # logger.info("returning wrapper_view = %s", wrapper_view)
    return wrapper_view


def test_view_deriver(view_callable, info):
    def derive_view(context, request):
        logger.debug("calling view")
        try:
            result = view_callable(context, request)
        except (AssertionError, TypeError, AttributeError, TemplateNotFound) as ex:
            logger.critical("Got exception from heptet_app.view callable.")
            logger.critical(ex)
            import traceback
            traceback.print_tb(sys.exc_info()[2])
            result = HTTPException("Got exception from heptet_app.view callable.", comment=str(ex),
                                   body_template=str(ex))

        logger.debug("view result is %s", result.status)
        return result

    return derive_view


def includeme(config):
    ## FIXME - create issue
    entity_view.options = ('operation', 'mapper_info', 'node_name', 'entry_point')
    config.add_view_deriver(entity_view, under=INGRESS)
#    config.add_view_deriver(test_view_deriver, over='mapped_view')
