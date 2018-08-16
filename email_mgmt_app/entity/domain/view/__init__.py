from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.view import view_config

from email_mgmt_app.entity.model.email_mgmt import Domain, Host
from email_mgmt_app.entity import EntityView, EntityCollectionView
from email_mgmt_app.views.default import munge_dict

def includeme(config: Configurator) -> None:
    # how do we further abstract this??
    config.add_view(".DomainView", route_name="DomainView",
                    renderer='templates/domain/domain.jinja2')
    config.add_route("DomainView", "/domainview/{id}")
    #config.add_view(domain_list_view, route_name='domain_list', renderer='templates/domain/domain_list.jinja2')
    #config.add_view(domain_list_view, renderer='json')

class DomainView(EntityView[Domain]):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)
        self._entity_type = Domain

class DomainCollectionView(EntityCollectionView[Domain]):
    pass

@view_config(route_name='domain_list', renderer='templates/domain/domain_list.jinja2')
@view_config(route_name='domain_list_json', renderer='json')
def domain_list_view(request: Request) -> dict:
    domains = request.dbsession.query(Domain).all()
    return munge_dict(request, {'domains': domains})


@view_config(route_name='domain_form', renderer='templates/domain/domain_form_main.jinja2')
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
