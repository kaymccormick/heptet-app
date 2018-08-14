from pyramid.request import Request
from pyramid.view import view_config
from views.default import munge_dict

@view_config(route_name='pubkeys', renderer='templates/pubkeys.jinja2')
def pubkeys_view(request: Request) -> dict:
    d = {}
    return munge_dict(request, d)
