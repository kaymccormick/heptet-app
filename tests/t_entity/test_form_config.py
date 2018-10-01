import logging

import pytest

from heptet_app import field_renderer
from sqlalchemy import inspect

import heptet_app.field_renderer
from heptet_app.entity import EntityFormConfiguration, EntityFormViewEntryPointGenerator
from heptet_app.model import map_column, get_column_map


logger = logging.getLogger(__name__)


def _map(what, *args, **kwargs):
    logger.critical("%s %s %s", what, args, kwargs)


@pytest.mark.integration
def test_form_config(generator_context_mock, process_struct_real):
    for x in process_struct_real.mappers:
        c = EntityFormConfiguration(x.entity,
                                    field_renderers=[])

    generator_context_mock.entity_form_config = c
    x = EntityFormViewEntryPointGenerator(generator_context_mock)

    #organization = inspect(Domain).relationships.organization
#    map_column(organization, field_renderer.Select)
#    logger.warning("%s", get_column_map(organization))

    # for x in process_struct.mappers:
    #     c = EntityFormConfiguration(x.entity,
    #                                 field_renderers=[{column.key:  field_renderer.__dict__[column.type.] for column in x.columns}
    #                                                  ]{'name': field_renderer.Text(),
    #                                                  'organization': field_renderer.Select()})
