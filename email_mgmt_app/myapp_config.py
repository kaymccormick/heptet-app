import logging

from pyramid.config import Configurator

from interfaces import IResource
from email_mgmt_app import RootResource

logger = logging.getLogger(__name__)


def includeme(config: Configurator):
    resource = RootResource()
    logger.warning("root resource is %s", resource)
    assert resource is not None
    config.registry.registerUtility(resource, IResource, 'root_resource')
    assert config.registry.queryUtility(IResource, 'root_resource') is not None
    # config.include(res)
