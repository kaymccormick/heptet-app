from pyramid.view import view_config

from email_mgmt_app.entity.model.email_mgmt import Domain, Host
from email_mgmt_app.entity import EntityView, EntityCollectionView
from email_mgmt_app.views.default import munge_dict
from heptet.web import Request

class DomainView(EntityView[Domain]):
    def __init__(self, request: Request = None, id: int=None) -> None:
        super().__init__(request, id)


class DomainCollectionView(EntityCollectionView[Domain]):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)


@view_config(route_name='domain_list', renderer='../templates/domain/domain_list.jinja2')
@view_config(route_name='domain_list_json', renderer='json')
def domain_list_view(request: Request) -> dict:
    domains = request.dbsession.query(Domain).all()
    return munge_dict(request, {'domains': domains})


@view_config(route_name='domain_form', renderer='../templates/domain/domain_form_main.jinja2')
def domain_form_view(request: Request) -> dict:
    hosts = request.dbsession.query(Host).all()
    return { 'hosts': hosts, 'r': request }


@view_config(route_name='domain', renderer='../templates/domain/domain_view.jinja2')
def domain_view(request: Request):
    domain = request.dbsession.query(Domain).filter(Domain.id == request.matchdict["id"]).first()
    return munge_dict(request, {"domain": domain })


@view_config(route_name='domain_create', renderer='../templates/domain/domain_create.jinja2')
def domain_create_view(request: Request):
    domain = Domain()
    domain.name = request.POST['domain_name']
    request.dbsession.add(domain)
    request.dbsession.flush()

    return munge_dict(request, { 'domain': domain })