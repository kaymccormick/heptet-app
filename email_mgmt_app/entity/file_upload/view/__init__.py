from pyramid.config import Configurator

from email_mgmt_app.entity.model.email_mgmt import FileUpload
from email_mgmt_app.res import ResourceManager, ResourceRegistration


class FileUploadView(object):
    pass


def includeme(config: Configurator):
    registration = ResourceRegistration('FileUpload', view=FileUploadView, entity_type=FileUpload)
    mgr = ResourceManager(config, registration)
    mgr.operation('up1oad', '.FileUploadView')
    config.add_resource_manager(mgr)

