from pyramid.request import Request
from pyramid.view import view_config
from views.default import munge_dict


@view_config(route_name='email_form', renderer='templates/email_address/email_form.jinja2')
def email_form_view(request: Request) -> dict:
    return munge_dict(request, {})
