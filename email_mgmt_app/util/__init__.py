import inspect
import logging
import sys

from pyramid.request import Request


def munge_dict(request: Request, indict: dict) -> dict:
    view_name = request.view_name
    context = request.context

    val = request.registry.settings['email_mgmt_app.request_attrs']
    logging.debug("attrs = %s", repr(val))
    attrs = val.split(', ')

    indict['r'] = { }
    for attr in attrs:
        indict['r'][attr] = request.__getattribute__(attr)

    #request.resource_path()

    stack = inspect.stack()
    class_ = stack[1][0].f_locals["self"].__class__
    indict['class_'] = class_
    if not "form" in indict.keys():
        indict["form"] = {}

    # try:
    #     if not "host_form" in indict["form"].keys():
    #         indict["form"]["host_form"] = host_form_defs(request)
    # except:
    #     logging.warning("unable to populate host_form_defs: %s", sys.exc_info()[1])

    try:
        if request.matched_route is not None and '_json' in request.matched_route.name:
            return indict
    except:
        logging.warning("unable to populate host_form_defs: %s", sys.exc_info()[1])

#    indict["r"] = request
    def x(*args, **kwargs):
        y = '#'
        try:
            y = request.route_path(*args, **kwargs)
        except:
            logging.warning("exception calling route_path %s", sys.exc_info()[1])

        return y

    indict["route_path"] = x

    return indict