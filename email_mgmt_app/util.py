import inspect
import logging
import sys
import urllib

from pyramid.renderers import get_renderer
from pyramid.request import Request





def render_template(request, template_name, d, nestlevel=0):
    #logging.critical("template = %s", template_name)
    renderer = get_renderer(template_name).template_loader()
    return renderer.render(d)


def get_exception_entry_point_key(exception):
    return 'exception_' + exception.__name__


def get_entry_point_key(request, resource, op_name):
    epstr = urllib.parse.unquote(request.resource_path(resource))
    epstr = epstr.replace('/', '_')
    if epstr[0] == '_':
        epstr = epstr[1:]
    if epstr[len(epstr) - 1] != '_':
        epstr = epstr + '_'
    epstr = epstr + op_name
    return epstr

