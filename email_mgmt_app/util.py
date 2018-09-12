import types
import urllib
from dataclasses import dataclass
from typing import Callable, AnyStr

from pyramid.renderers import get_renderer
from zope.interface.registry import Components


def render_template(request, template_name, d, nestlevel=0):
    # logging.critical("template = %s", template_name)
    renderer = get_renderer(template_name).template_loader()
    return renderer.render(d)


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


def _dump(v, line_prefix=None, name_prefix="", depth=0, cb: Callable = None, recurse=True):
    if line_prefix is None:
        line_prefix = "  " * depth

    vv = None
    if isinstance(v, types.ModuleType):
        vv = "<module '%s'>" % v.__name__
    if vv is None:
        vv = str(v)
    cb("%s%s = %s", line_prefix, name_prefix[0:-1], vv)
    if depth >= 5 or not recurse:
        return
    if isinstance(v, types.ModuleType):
        pass  # cb("%s: module %s", lineprefix, v)
    elif isinstance(v, Components):
        for x in v.registeredUtilities():
            _dump(x, None, "%s%s." % (name_prefix, "utility"), depth + 1, cb, recurse=False)
        #     _dump(x, None, "%s%s." % (nameprefix, "utility"), depth + 1, cb)
        pass
    elif hasattr(v, "__dict__"):
        for x, y in v.__dict__.items():
            if not x.startswith('_'):
                # cb("%s%s%s = %s", lineprefix, nameprefix, x, y)
                _dump(y, name_prefix="%s%s." % (name_prefix, x), depth=depth + 1, cb=cb)
    else:
        return


def get_template(env, name):
    @dataclass
    class _info:
        name: AnyStr
        package: AnyStr=None

    return env(_info(name))
