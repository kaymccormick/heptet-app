import ldap
from pyramid.request import Request
from pyramid.view import view_config

from email_mgmt_app.entity import EntityView
from email_mgmt_app.entity.model.email_mgmt import Domain, Host


class HostView(EntityView[Host]):
    pass


@view_config(route_name='host_form', renderer='../templates/host/host_form_main.jinja2')
def host_form_view(request: Request) -> dict:
    hosts = request.dbsession.query(Host).all()
    return { 'hosts': hosts, 'r': request }


@view_config(route_name='host_list', renderer='../templates/host/host_list_main.jinja2')
def host_list_view(request: Request) -> dict:
    hosts = request.dbsession.query(Host).all()
    return { 'hosts': hosts, 'r': request }


@view_config(route_name='host', renderer='../templates/host/host.jinja2')
def host_view(request: Request):
    host = request.dbsession.query(Host).filter(Host.id == request.matchdict["id"]).first()
    return munge_dict(request, { "host": host })


def host_form_defs(request):
    return { "action": request.route_path('host_create') }


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