import logging

from pyramid.viewderivers import INGRESS

from email_mgmt_app.entity import BaseEntityRelatedView
from email_mgmt_app.util import munge_dict
from email_mgmt_app.entity.view import BaseView


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
    if et is None:
        return view
    operation = info.options.get('operation')

    def wrapper_view(context, request):
        logging.info("original view = %s", repr(info.original_view))
        original_view = info.original_view

        renderer = None
        if issubclass(original_view, BaseView):
            original_view.operation = operation

        if issubclass(original_view, BaseEntityRelatedView):
            # is this still in effect?
            original_view.entity_type = et

        if renderer:
            request.override_renderer = renderer

        response = view(context, request)
        return response

    logging.info("returning wrapper_view = %s", wrapper_view)
    return wrapper_view


def includeme(config):
    entity_view.options = ('operation',)
    config.add_view_deriver(entity_view)
#    config.add_view_deriver(munge_view)


