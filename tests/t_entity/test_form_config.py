import logging

from email_mgmt_app import field_renderer
from sqlalchemy import inspect

import email_mgmt_app.field_renderer
from email_mgmt_app.entity import EntityFormConfiguration, EntityFormViewEntryPointGenerator
from email_mgmt_app.model import map_column, get_column_map
from email_mgmt_app.model.email_mgmt import Domain

logger = logging.getLogger(__name__)


def _map(what, *args, **kwargs):
    logger.critical("%s %s %s", what, args, kwargs)


def test_form_config(generator_context_mock, process_struct_real):
    for x in process_struct_real.mappers:
        c = EntityFormConfiguration(x.entity,
                                    field_renderers=[])

    generator_context_mock.entity_form_config = c
    x = EntityFormViewEntryPointGenerator(generator_context_mock)

    organization = inspect(Domain).relationships.organization
    map_column(organization, field_renderer.Select)
    logger.warning("%s", get_column_map(organization))

    # for x in process_struct.mappers:
    #     c = EntityFormConfiguration(x.entity,
    #                                 field_renderers=[{column.key:  field_renderer.__dict__[column.type.] for column in x.columns}
    #                                                  ]{'name': field_renderer.Text(),
    #                                                  'organization': field_renderer.Select()})
