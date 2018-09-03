import inspect
import logging
import sys

from pyramid.renderers import get_renderer
from pyramid.request import Request



# def munge_dict(request: Request, indict: dict) -> dict:
#     val = request.registry.settings['email_mgmt_app.request_attrs']
#     attrs = val.split(', ')
#
#     indict['r'] = { }
#     for attr in attrs:
#         indict['r'][attr] = request.__getattribute__(attr)
#
#     if not "form" in indict.keys():
#         indict["form"] = {}
#
#     # try:
#     #     if not "host_form" in indict["form"].keys():
#     #         indict["form"]["host_form"] = host_form_defs(request)
#     # except:
#     #     logging.warning("unable to populate host_form_defs: %s", sys.exc_info()[1])
#
#     try:
#         if request.matched_route is not None and '_json' in request.matched_route.name:
#             return indict
#     except:
#         logging.warning("unable to populate host_form_defs: %s", sys.exc_info()[1])
#
# #    indict["r"] = request
#     def x(*args, **kwargs):
#         y = '#'
#         try:
#             y = request.route_path(*args, **kwargs)
#         except:
#             logging.warning("exception calling route_path %s", sys.exc_info()[1])
#
#         return y
#
#     indict["route_path"] = x
#
#     return indict


def render_template(request, template_name, d, nestlevel=0):
    #logging.critical("template = %s", template_name)
    renderer = get_renderer(template_name).template_loader()
    return renderer.render(d)


def get_exception_entry_point_key(exception):
    return 'exception_' + exception.__name__


def get_entry_point_key(request, resource, op_name):
    epstr = request.resource_path(resource).replace('/', '_')
    if epstr[0] == '_':
        epstr = epstr[1:]
    if epstr[len(epstr) - 1] != '_':
        epstr = epstr + '_'
    epstr = epstr + op_name
    return epstr

