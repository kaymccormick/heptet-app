from typing import TypeVar, Generic

import ldap
from ldap.ldapobject import LDAPObject
from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.security import remember, forget, Allow, Authenticated
from pyramid.view import view_config, forbidden_view_config
from pyramid_ldap import get_ldap_connector
from sqlalchemy import desc, func

from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Query

from email_mgmt_app.models.mymodel import Domain, Host, ServiceEntry


class BaseView(object):
    def __init__(self, request: Request=None) -> None:
        self._request = request

    @property
    def request(self) -> Request:
        return self._request


BaseEntityRelatedView_RelatedEntityType = TypeVar('BaseEntityRelatedView_RelatedEntityType')
class BaseEntityRelatedView(Generic[BaseEntityRelatedView_RelatedEntityType], BaseView):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)

EntityView_EntityType = TypeVar('EntityView_EntityType')
class EntityView(BaseEntityRelatedView[EntityView_EntityType]):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)


class DomainView(EntityView[Domain]):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)

EntityCollectionView_EntityType = TypeVar('EntityCollectionView_EntityType')
class EntityCollectionView(BaseEntityRelatedView[EntityCollectionView_EntityType]):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)

class DomainCollectionView(EntityCollectionView[Domain]):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)


@view_config(route_name='domain_list', renderer='../templates/domain/domain_list.jinja2')
@view_config(route_name='domain_list_json', renderer='json')
def domain_list_view(request: Request) -> dict:
    domains = request.dbsession.query(Domain).all()
    return munge_dict(request, {'domains': domains})

@view_config(route_name='host_form', renderer='../templates/host/host_form_main.jinja2')
def host_form_view(request: Request) -> dict:
    hosts = request.dbsession.query(Host).all()
    return { 'hosts': hosts, 'r': request }

@view_config(route_name='domain_form', renderer='../templates/domain/domain_form_main.jinja2')
def domain_form_view(request: Request) -> dict:
    hosts = request.dbsession.query(Host).all()
    return { 'hosts': hosts, 'r': request }


@view_config(route_name='service', renderer='../templates/service/service.jinja2')
def service_view(request: Request) -> dict:
    service = request.dbsession.query(ServiceEntry).filter(ServiceEntry.id == request.matchdict['id']).first()
    hosts = request.dbsession.query(Host).all()
    return { 'service': service, 'hosts': hosts, 'r': request }

@view_config(route_name='service_list', renderer='../templates/service/service_list.jinja2')
def service_list_view(request: Request) -> dict:
    entry__all = request.dbsession.query(ServiceEntry).order_by(ServiceEntry.port_num, ServiceEntry.protocol_name).all()
    hosts = request.dbsession.query(Host).all()
    return { 'services': entry__all , 'hosts': hosts, 'r': request }


@view_config(route_name='host_list', renderer='../templates/host/host_list_main.jinja2')
def host_list_view(request: Request) -> dict:
    hosts = request.dbsession.query(Host).all()
    return { 'hosts': hosts, 'r': request }

@view_config(route_name='main', renderer='../templates/main_child.jinja2')
def main_view(request: Request) -> dict:
    q = request.dbsession.query(Host) # type: Query
    need_paths_for = ['service_list']
    paths = { }
    for path in need_paths_for:
        paths[path] = request.route_path("service_list")

    if q.count() == 0:
        hosts = [ ]
    else:
        hosts = q.all()
    return { 'hosts': hosts, 'paths': paths, 'r': request }

@view_config(route_name='host', renderer='../templates/host/host.jinja2')
def host_view(request: Request):
    host = request.dbsession.query(Host).filter(Host.id == request.matchdict["id"]).first()
    return munge_dict(request, { "host": host })

@view_config(route_name='domain', renderer='../templates/domain/domain_view.jinja2')
def domain_view(request: Request):
    domain = request.dbsession.query(Domain).filter(Domain.id == request.matchdict["id"]).first()
    return munge_dict(request, {"domain": domain })


# @view_config(route_name='port_register_form', renderer='../templates/port_registeR_form.jinja2')
# def port_register_form(request):
#     pass

def host_form_defs(request):
    return { "action": request.route_path('host_create') }

def munge_dict(request: Request, indict: dict) -> dict:

    if not "form" in indict.keys():
        indict["form"] = {}

    if not "host_form" in indict["form"].keys():
        indict["form"]["host_form"] = host_form_defs(request)

    if not '_json' in request.matched_route.name:
        indict["r"] = request

    return indict

@view_config(route_name='host_create', renderer='../templates/host/host_create.jinja2')
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

    host = Host()
    host.domain = domain
    host.name = hostname_
    request.dbsession.add(host)
    request.dbsession.flush()

    return munge_dict(request, { 'host': host, 'domain': domain })

@view_config(route_name='domain_create', renderer='../templates/domain/domain_create.jinja2')
def domain_create_view(request: Request):
    domain = Domain()
    domain.name = request.POST['domain_name']
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


