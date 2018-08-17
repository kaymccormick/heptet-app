from email_mgmt_app.context import EntityResource
from pyramid.config import Configurator
from pyramid.request import Request

from email_mgmt_app.entity.model.email_mgmt import Domain, Host, Organization
from email_mgmt_app.entity import EntityView, EntityCollectionView, EntityFormView
from email_mgmt_app.views.default import munge_dict

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
    config.register_resource('Domain', Domain)
    
    config.add_view(".DomainView", name='view', context=EntityResource,
                    renderer='templates/domain/domain.jinja2')

    config.add_view('.DomainFormView', route_name='domain_form',
                    renderer='templates/domain/domain_form_main.jinja2')

    config.add_route('domain_form', '/domain_form')

    config.add_view(".DomainCollectionView", name='', context=EntityResource,
                    entity_name='Domain',
                    renderer='templates/domain/collection.jinja2')


class DomainView(EntityView[Domain]):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)
        self._entity_type = Domain


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


@view_config(route_name='domain', renderer='templates/domain/domain.jinja2')
def domain_view(request: Request):
    domain = request.dbsession.query(Domain).filter(Domain.id == request.matchdict["id"]).first()
    return munge_dict(request, {"domain": domain })


@view_config(route_name='domain_create', renderer='templates/domain/domain_create.jinja2')
def domain_create_view(request: Request):
    domain = Domain()
    domain.name = request.POST['domain_name']
    request.dbsession.add(domain)
    request.dbsession.flush()

    return munge_dict(request, { 'domain': domain })
