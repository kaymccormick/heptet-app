from pyramid.request import Request

from email_mgmt_app.entity import EntityCollectionView
from email_mgmt_app.entity.model.email_mgmt import Organization
from pyramid.config import Configurator


def includeme(config: Configurator) -> None:
    config.add_view(".OrganizationCollectionView",
                    route_name='organization_collection',
                    renderer='templates/organization/collection.jinja2')
    config.add_route('organization_collection', '/organizations')


class OrganizationCollectionView(EntityCollectionView[Organization]):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)
        self._entity_type = Organization

