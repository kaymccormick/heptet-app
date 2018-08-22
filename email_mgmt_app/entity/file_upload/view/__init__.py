from pyramid.config import Configurator

from email_mgmt_app.entity.model.email_mgmt import FileUpload
from res.resource import ResourceManager, ResourceRegistration


class FileUploadView(object):
    pass


def includeme(config: Configurator):
    mgr = ResourceManager(config, FileUpload)
    config.register_resource(ResourceRegistration('FileUpload', view=FileUploadView, entity_type=FileUpload), mgr)
    mgr.operation('up1oad', '.FileUploadView')
