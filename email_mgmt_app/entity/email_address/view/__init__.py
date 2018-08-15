from entity.model.email_mgmt import Host
from pyramid.request import Request
from pyramid.view import view_config
from views.default import munge_dict


@view_config(route_name='email_form', renderer='templates/email_address/email_form.jinja2')
def email_form_view(request: Request) -> dict:
    d = {'hosts': request.dbsession.query(Host).all()}
    return munge_dict(request, {})

@view_config(route_name='email_create', renderer='templates/email_address/email_create.jinja2')
def email_create_view(request: Request) -> dict:
    return munge_dict(request, {})

