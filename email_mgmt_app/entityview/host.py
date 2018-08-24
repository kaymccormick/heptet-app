import logging

from pyramid.config import Configurator
from sqlalchemy import Table, Integer
from sqlalchemy.engine import reflection
from sqlalchemy.orm import Session

from email_mgmt_app.entity.model.meta import Base
from pyramid.request import Request

from email_mgmt_app.entity import EntityView, EntityCollectionView, EntityFormView
from email_mgmt_app.entity.model.email_mgmt import Host
from email_mgmt_app.util import munge_dict
from email_mgmt_app.res import ResourceRegistration, Resource, ResourceManager, OperationArgument



class HostView(EntityView[Host]):
    pass


class HostCollectionView(EntityCollectionView[Host]):
    pass


class HostFormView(EntityFormView[Host]):
    pass

#@view_config(route_name='host_form', renderer='templates/host/form.jinja2')
def host_form_view(request: Request) -> dict:
    hosts = request.dbsession.query(Host).all()
    return { 'hosts': hosts, 'route_path': request.route_path }


#@view_config(route_name='host_list', renderer='templates/host/list.jinja2')
def host_list_view(request: Request) -> dict:
    hosts = request.dbsession.query(Host).all()
    return { 'hosts': hosts, 'route_path': request.route_path }


#@view_config(route_name='host', renderer='templates/host/view.jinja2')
def host_view(request: Request):
    dbsession = request.dbsession # type: Session
    host = dbsession.query(Host).filter(Host.id == request.matchdict["id"]).first()
    return munge_dict(request, { "host": host })

#@view_config(route_name='generic', renderer='templates/generic.jinja2')
def generic_view(request: Request):
    dbsession = request.dbsession # type: Session
    i = reflection.Inspector.from_engine(dbsession.get_bind())
    for t in Base.metadata.sorted_tables:
        print(t.name)

    d = { }
    d['tables'] = i.get_table_names()
    d['columns'] = { }
    d['tables2'] = {}
    for table in i.get_table_names():
        table1 = Table(table, Base.metadata, autoload=True, autoload_with=dbsession.get_bind())
        d['tables2'][table] = table1
        d['columns'][table] = i.get_columns(table)

    e = munge_dict(request, d)
    logging.info("%s" % repr(e))
    return e


#@view_config(route_name='host_create', renderer='templates/host/host_create.jinja2')
def host_create_view(request: Request):
    #conn = ldap.initialize("ldap://10.8.0.1") # type: LDAPObject
    # r = conn.search_s("dc=heptet,dc=us", ldap.SCOPE_SUBTREE, '(objectClass=posixAccount)')
    # print(r)
    hostname_ = request.POST['hostname'] # type: str
    split = hostname_.split('.')
    reverse = reversed(split)
    tld = next(reverse)
    host_name = next(reverse) + "." + tld
    host = request.dbsession.query(Host).filter(Host.name == host_name).first()
    if host is None:
        host = Host()
        host.name = host_name;

    host = Host()
    host.host = host
    host.name = hostname_
    request.dbsession.add(host)
    request.dbsession.flush()

    return munge_dict(request, { 'host': host, 'host': host })

def includeme(config: Configurator):
    registration = ResourceManager.reg('Host', default_view=HostView, entity_type=Host)
    mgr = ResourceManager(config, registration)
    mgr.operation('view', HostView, [OperationArgument("id", Integer)])
    mgr.operation('list', HostCollectionView, [])
    mgr.operation('form', HostFormView, [])
    config.add_resource_manager(mgr)

    # config.add_view(".HostView", name='view', context=Resource,
    #                 entity_type=Host,
    #                 renderer='templates/host/view.jinja2')

    # config.add_view('.HostFormView', name='form',
    #                 renderer='templates/host/form.jinja2')
    #
    # config.add_view(".HostCollectionView", name='list', context=ContainerResource,
    #                 entity_name='Host',
    #                 renderer='templates/host/collection.jinja2')

