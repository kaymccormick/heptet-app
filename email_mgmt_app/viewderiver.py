import logging

from pyramid.tweens import INGRESS

from email_mgmt_app.entity import BaseEntityRelatedView
from email_mgmt_app.view import BaseView
from email_mgmt_app.util import munge_dict


def munge_view(view, info):
    def wrapper_view(context, request):
        original_view = info.original_view
        response = view(context, request)

        if '__getattr__' in response.__dict__:
            response = munge_dict(request, response)

        return response
    return wrapper_view


def entity_view(view, info):
    et = info.options.get('entity_type')

    operation = info.options.get('operation')
    inspect = info.options.get('inspect')

    info.registry.email_mgmt_app.views.append(info)

    logging.debug("entity_view %s", info.original_view)
    def wrapper_view(context, request):
        logging.info("original view = %s", repr(info.original_view))
        original_view = info.original_view

        renderer = None
        if isinstance(original_view, type):
            if issubclass(original_view, BaseView):
                original_view.operation = operation
                original_view.entry_point_key = info.options['entry_point_key']

            if issubclass(original_view, BaseEntityRelatedView):
                # is this still in effect? (why wouldn't it be in effect?)

                logging.warning("setting entity_type to %s (orig = %s)", et, str(original_view.entity_type))
                original_view.entity_type = et
                #original_view.inspect = inspect

        if renderer:
            request.override_renderer = renderer

        response = view(context, request)
        return response

    #logging.info("returning wrapper_view = %s", wrapper_view)
    return wrapper_view


def includeme(config):
    entity_view.options = ('operation','inspect','entry_point_key','node_name')
    config.add_view_deriver(entity_view,under=INGRESS)
    config.add_view_deriver(munge_view, under='owrapped_view')
