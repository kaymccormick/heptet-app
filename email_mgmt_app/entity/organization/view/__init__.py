from pyramid.request import Request

from email_mgmt_app.entity import EntityCollectionView, EntityView
from email_mgmt_app.entity.model.email_mgmt import Organization
from pyramid.config import Configurator


def includeme(config: Configurator) -> None:
    config.add_view(".OrganizationCollectionView",
                    route_name='organization_collection',
                    renderer='templates/organization/collection.jinja2')
    config.add_route('organization_collection', '/organizations')
    config.add_view(".OrganizationView",
                    route_name='organization',
                    renderer='templates/organization/entity.jinja2')
    config.add_route('organization', '/organization/{id}')

class OrganizationCollectionView(EntityCollectionView[Organization]):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)
        self._entity_type = Organization


class OrganizationView(EntityView[Organization]):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)
        self._entity_type = Organization