from sqlalchemy import Table, inspect
from sqlalchemy.orm import Mapper

import field_renderer
from entity import EntityFormConfiguration, EntityFormViewEntryPointGenerator
import logging

from model import map_column, get_column_map
from model.email_mgmt import Domain
from model.meta import metadata

logger = logging.getLogger(__name__)


def _map(what, *args, **kwargs):
    logger.critical("%s %s %s", what, args, kwargs)


def test_form_config(my_gen_context, process_struct_real):
    # for x in process_struct.mappers:
    #     c = EntityFormConfiguration(x.entity,
    #                                 field_renderers=[{column.key:  field_renderer.__dict__[column.type.] for column in x.columns}
    #                                                  ]{'name': field_renderer.Text(),
    #                                                  'organization': field_renderer.Select()})
    # my_gen_context.entity_form_config = c
    # x = EntityFormViewEntryPointGenerator(my_gen_context)
    # logger.critical("%s", x)
    # logger.critical("%s", c.entity_type)
    # logger.critical("%s", c)
    organization = inspect(Domain).relationships.organization
    map_column(organization, field_renderer.Select)
    logger.warning("%s", get_column_map(organization))
