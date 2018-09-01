import logging

from pyramid.config import Configurator
from sqlalchemy.event import listen
from sqlalchemy.orm import Mapper

logger = logging.getLogger(__name__)

# is this mostly / all sqlalchemy events?
# it looks like the events have been moved

def includeme(config: Configurator):
    def add_mapper(config: Configurator, mapper: Mapper):
        config.registry.email_mgmt_app.mappers[mapper.mapped_table.key] = mapper

    config.add_directive('add_mapper', add_mapper)
