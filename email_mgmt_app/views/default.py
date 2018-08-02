from pyramid.request import Request
from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from email_mgmt_app.models.mymodel import Domain


def host_form_defs(request):
    return { "action": request.route_path('host_create') }

def munge_dict(request, indict: dict) -> dict:
    if not "form" in indict.keys():
        indict["form"] = {}

    if not "host_form" in indict["form"].keys():
        indict["form"]["host_form"] = host_form_defs(request)

    return indict

@view_config(route_name='host_create', renderer='../templates/host_create.jinja2')
def host_create_view(request: Request):
    hostname_ = request.POST['hostname'] # type: str
    split = hostname_.split('.')
    reverse = reversed(split)
    tld = next(reverse)
    domain_name = next(reverse) + "." + tld
    domain = request.dbsession.query(Domain).filter(Domain.name == domain_name).first()
    if domain is None:
        domain = Domain()
        domain.name = domain_name;
        request.dbsession.add(domain)

    return munge_dict(request, { 'domain': domain })


@view_config(route_name='home', renderer='../templates/mytemplate.jinja2')
def my_view(request):
    try:
        pass
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    return munge_dict(request, {'project': 'Pyramid Scaffold'})


db_err_msg = "Pyramid is having a problem using your SQL database."

