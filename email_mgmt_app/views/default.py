import ldap
from ldap.ldapobject import LDAPObject
from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.security import remember, forget, Allow, Authenticated
from pyramid.view import view_config, forbidden_view_config
from pyramid_ldap import get_ldap_connector

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
    conn = ldap.initialize("ldap://10.8.0.1") # type: LDAPObject
    # r = conn.search_s("dc=heptet,dc=us", ldap.SCOPE_SUBTREE, '(objectClass=posixAccount)')
    # print(r)
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
        request.dbsession.flush()

    return munge_dict(request, { 'domain': domain })



db_err_msg = "Pyramid is having a problem using your SQL database."

@view_config(route_name='login',
             renderer='../templates/login.jinja2')
@forbidden_view_config(renderer='../templates/login.jinja2')
def login(request):
    url = request.current_route_url()
    login = ''
    password = ''
    error = ''

    if 'form.submitted' in request.POST:
        login = request.POST['login']
        password = request.POST['password']
        connector = get_ldap_connector(request)
        data = connector.authenticate(login, password)
        if data is not None:
            dn = data[0]
            headers = remember(request, dn)
            return HTTPFound('/', headers=headers)
        else:
            error = 'Invalid credentials'

    return dict(
        login_url=url,
        login=login,
        password=password,
        error=error,
        )

@view_config(route_name='root', permission='view')
def logged_in(request):
    return Response('OK')

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return Response('Logged out', headers=headers)


