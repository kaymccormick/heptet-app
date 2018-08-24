from pyramid.config import Configurator

from email_mgmt_app.entity.model.email_mgmt import FileUpload
from email_mgmt_app.res import ResourceManager, ResourceRegistration
from email_mgmt_app.entity import BaseEntityRelatedView


class FileUploadView(BaseEntityRelatedView[FileUpload]):
    pass


def includeme(config: Configurator):
    registration = ResourceManager.reg('FileUpload', default_view=FileUploadView, entity_type=FileUpload)
    mgr = ResourceManager(config, registration)
    mgr.operation('upload', FileUploadView, [])
    config.add_resource_manager(mgr)

