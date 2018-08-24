
from email_mgmt_app.res import ResourceRegistration, Resource, ResourceManager, OperationArgument
from pyramid.config import Configurator
from pyramid.request import Request

from email_mgmt_app.entity.model.email_mgmt import Domain, Host, Organization
from email_mgmt_app.entity import EntityView, EntityCollectionView, EntityFormView
from email_mgmt_app.util import munge_dict
from email_mgmt_app.res import SubpathArgumentGetter
from email_mgmt_app.type import Integer
from email_mgmt_app.res import ArgumentGetter

class DomainView(EntityView[Domain]):
    pass


class DomainCollectionView(EntityCollectionView[Domain]):
    pass

class DomainFormView(EntityFormView[Domain]):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)
        self._entity_type = Domain

    def __call__(self, *args, **kwargs):
        hosts = self.request.dbsession.query(Host).all()
        orgs = self.request.dbsession.query(Organization).all()
        return munge_dict(self.request, {'hosts': hosts, 'orgs': orgs})

def domain_form_view(request: Request) -> dict:
    hosts = request.dbsession.query(Host).all()
    return munge_dict(request, { 'hosts': hosts })


#@view_config(route_name='domain', renderer='templates/domain/domain.jinja2')
def domain_view(request: Request):
    domain = request.dbsession.query(Domain).filter(Domain.id == request.matchdict["id"]).first()
    return munge_dict(request, {"domain": domain })


#@view_config(route_name='domain_create', renderer='templates/domain/domain_create.jinja2')
def domain_create_view(request: Request):
    domain = Domain()
    domain.name = request.POST['domain_name']
    request.dbsession.add(domain)
    request.dbsession.flush()

    return munge_dict(request, { 'domain': domain })

def includeme(config: Configurator) -> None:
    registration = ResourceManager.reg('Domain', default_view=DomainView, entity_type=Domain)
    mgr = ResourceManager(config, registration)

    mgr.operation('view', DomainView,
                  [OperationArgument(
                      "id", Integer,
                      getter=ArgumentGetter())])

    mgr.operation('form', DomainFormView, [])
    mgr.operation('list', DomainCollectionView, [])
    config.add_resource_manager(mgr)



