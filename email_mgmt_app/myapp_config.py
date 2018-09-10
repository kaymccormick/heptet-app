import json
import logging
import os

from marshmallow import ValidationError
from pyramid.config import Configurator
from sqlalchemy import String
from sqlalchemy.exc import InvalidRequestError

import res
from db_dump import get_process_schema
from db_dump.info import ProcessStruct
from entity import EntityFormView
from impl import MapperWrapper
from interfaces import IMapperInfo, IResource
from res import ResourceManager, OperationArgument, RootResource

logger = logging.getLogger(__name__)


def config_process_struct(config, process):
    for mapper in process.mappers:
        wrapper = MapperWrapper(mapper)
        logger.debug("Registering mapper_wrapper %s", mapper)
        config.registry.registerUtility(wrapper, IMapperInfo, wrapper.key)
        node_name = mapper.local_table.key
        manager = ResourceManager(
            config,
            wrapper.key,
            node_name=node_name,
            mapper_wrapper=wrapper
        )

        manager.operation(name='form', view=EntityFormView,
                          args=[OperationArgument.SubpathArgument('action', String, default='create')])
        config.add_resource_manager(manager)


def load_process_struct() -> ProcessStruct:
    relpath = os.path.join(os.path.dirname(__file__), "email_db.json")
    logger.critical("%s", __file__)
    email_db_json = ''
    # we need to find this?
    with open(relpath, 'r') as f:
        email_db_json = ''.join(f.readlines())
    process_schema = get_process_schema()
    process = None  # type: ProcessStruct

    # logger.debug("json for db is %s", email_db_json)
    try:
        process = process_schema.load(json.loads(email_db_json))
        logger.debug("process = %s", repr(process))
    except InvalidRequestError as ex:
        logger.critical("Unable to load database json.")
        logger.critical(ex)
        raise ex
    except ValidationError as ve:
        # todo better error handling
        for k, v in ve.messages.items():
            logger.critical("input error in %s: %s", k, v)
        raise ve
    return process


def includeme(config: Configurator):
    resource = RootResource()
    logger.warning("root resource is %s", resource)
    assert resource is not None
    config.registry.registerUtility(resource, IResource, 'root_resource')
    assert config.registry.queryUtility(IResource, 'root_resource') is not None
    config.include(res)
