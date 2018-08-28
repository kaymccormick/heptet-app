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

    def after_configured():
        logging.info("after_configured")
        # for k, v in config.registry.email_mgmt_app.mappers.items():
        #     logging.warning("%s = %s", k, v)

    listen(Mapper, 'after_configured', after_configured)
    config.action(None, action)
