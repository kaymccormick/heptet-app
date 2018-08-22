from pyramid.request import Request

from email_mgmt_app.entity import EntityCollectionView, EntityView, EntityFormView, EntityFormActionView
from email_mgmt_app.entity.model.email_mgmt import Organization
from pyramid.config import Configurator

from email_mgmt_app.res import ResourceRegistration, ResourceManager


def includeme(config: Configurator) -> None:
    mgr = ResourceManager(config, Organization)
    config.register_resource\
        (ResourceRegistration('Organization', view=OrganizationView, entity_type=Organization),
         mgr)

#    config.add_view(".OrganizationCollectionView",
#                     route_name='organization_collection',
#                     renderer='templates/organization/collection.jinja2')
#    config.add_route('organization_collection', '/organizations')
#     config.add_view(".OrganizationView",
#                     route_name='organization',
#                     renderer='templates/organization/entity.jinja2')
#    config.add_route('organization', '/organization/{id}')
#     config.add_view(".OrganizationForm", route_name="organization_form",
#                      renderer='templates/organization/form.jinja2')
#     #config.add_route('organization_form', '/organizations/form/{parent_id}')
#     config.add_view('.OrganizationFormAction', route_name='organization_form_action',
#                     renderer='templates/organization/form_action.jinja2')
#     #config.add_route('organization_form_action', '/organizations/form/action')
#

class OrganizationCollectionView(EntityCollectionView[Organization]):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)
        self._entity_type = Organization


class OrganizationView(EntityView[Organization]):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)
        self._entity_type = Organization


class OrganizationForm(EntityFormView[Organization]):
    pass


class OrganizationFormAction(EntityFormActionView[Organization]):
    pass

