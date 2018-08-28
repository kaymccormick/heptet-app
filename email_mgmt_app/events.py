import logging

from pyramid.config import Configurator
from sqlalchemy.event import listen
from sqlalchemy.orm import Mapper

# is this mostly / all sqlalchemy events?




def includeme(config: Configurator):
    def action():
        pass

    def add_mapper(config: Configurator, mapper: Mapper):
        config.registry.email_mgmt_app.mappers[mapper.mapped_table.key] = mapper

    config.add_directive('add_mapper', add_mapper)

    config.action(None, action)
