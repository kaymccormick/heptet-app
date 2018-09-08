import logging

from pyramid.config import Configurator

import email_mgmt_app.myapp_config
from email_mgmt_app.myapp_config import config_process_struct, load_process_struct
from email_mgmt_app.interfaces import IResource
from email_mgmt_app.res import RootResource

logger = logging.getLogger(__name__)


def test_config_process_struct(process_struct, config_fixture):
    config_process_struct(config_fixture, process_struct)


def test_load_process_struct():
    load_process_struct()



def test_config(config_fixture):
    c = config_fixture
    logger.warning("c = %s", c)
    assert c.registry.queryUtility(IResource, 'root_resource') is not None

def test_config_2():
    config = Configurator()
    config.include(email_mgmt_app.myapp_config.includeme)
    assert config.registry.queryUtility(IResource, 'root_resource') is not None