from ....resource import EntityResource, ResourceRegistration, Resource, ResourceManager
from pyramid.config import Configurator
from pyramid.request import Request

from email_mgmt_app.entity.model.email_mgmt import Domain, Host, Organization
from email_mgmt_app.entity import EntityView, EntityCollectionView, EntityFormView
from email_mgmt_app.util import munge_dict

from pyramid.httpexceptions import HTTPFound
from pyramid.security import (
    remember,
    forget,
    )

from pyramid.view import (
    view_config,
    view_defaults
    )

from email_mgmt_app.security import (
    USERS,
    check_password
)


def includeme(config: Configurator) -> None:
    mgr = ResourceManager(config, Domain)
    config.register_resource\
        (ResourceRegistration('Domain', view=DomainView, entity_type=Domain),
         mgr)

    mgr.operation('view', ".DomainView")
    config.add_view(".DomainView", name='view', context=Resource,
                    entity_type=Domain,
                    )

    mgr.operation('form', ".DomainFormView")
    config.add_view('.DomainFormView', name='form',
                    context=Resource, entity_type=Domain)

    mgr.operation('list', ".DomainCollectionView")
    config.add_view(".DomainCollectionView", name='list', context=Resource,
                     entity_type=Domain)


class DomainView(EntityView[Domain]):
    pass

class DomainCollectionView(EntityCollectionView[Domain]):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)
        self._entity_type = Domain


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
