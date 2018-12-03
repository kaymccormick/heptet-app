import types
import urllib
from typing import Callable, AnyStr

from pyramid.renderers import get_renderer
from zope.interface.registry import Components

import logging

logger = logging.getLogger(__name__)


def get_exception_entry_point_key(exception):
    x = getattr(exception, "__name__", None) or exception.__class__.__name__
    return 'exception_' + x


def get_entry_point_key(request, resource, op_name):
    epstr = urllib.parse.unquote(request.resource_path(resource))
    epstr = epstr.replace('/', '_')
    if epstr[0] == '_':
        epstr = epstr[1:]
    if epstr[len(epstr) - 1] != '_':
        epstr = epstr + '_'
    epstr = epstr + op_name
    return epstr


def _dump(v, line_prefix="", name_prefix="", depth=0, cb: Callable = None, recurse=True):

    line_prefix = "  " * depth + (line_prefix or "")

    vv = None
    if isinstance(v, types.ModuleType):
        vv = "<module '%s'>" % v.__name__
    if vv is None:
        #vv = "{:compact}".format(v)
        vv = str(v)
    cb("%s%s = %s", line_prefix, name_prefix[0:-1], vv)
    if depth >= 5 or not recurse:
        return
    if isinstance(v, types.ModuleType):
        pass  # cb("%s: module %s", lineprefix, v)
    elif isinstance(v, Components):
        for x in v.registeredUtilities():
            #_dump(x, None, line_prefix, depth + 1, cb, recurse=False)
            _dump(x, None, line_prefix, depth + 1, cb)
        pass
    elif hasattr(v, "__dict__"):
        for x, y in v.__dict__.items():
            if not x.startswith('_'):
                pass
                # cb("%s%s%s = %s", lineprefix, nameprefix, x, y)
                #_dump(y, name_prefix="%s%s." % (name_prefix, x), depth=depth + 1, cb=cb)
    else:
        return


# def format_discriminator(l, *elems):
#     for elem in elems:
#         if hasattr(elem, "discriminator"):
#             result = elem.discriminator
#             format_discriminator(l, *result)
#             #logger.debug("%s.discriminator = %r", elem, result)
#         else:
#             prepend = False
# #            logger.warning("%s", elem.__class__.__name__)
#             try:
#                 prepend = elem.is_element_entry()
#             except AttributeError as ex:
# #                logger.critical(ex)
#                 pass
#             finally:
#                 pass
#
#             l.append((prepend and '/' or '') + str(elem))
#
