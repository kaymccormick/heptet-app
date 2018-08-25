import logging

from pyramid.config import Configurator
from sqlalchemy.event import listen
from sqlalchemy.orm import Mapper


def includeme(config: Configurator):
    mappers = {}

    # standard decorator style
    def receive_mapper_configured(mapper: Mapper, *args, **kwargs):
        "listen for the 'mapper_configured' event"
        logging.critical("omg mapper configured %s, %s", repr(args), repr(kwargs))

        mappers[mapper.mapped_table.key] = mapper
        # ... (event handling logic) ...

    listen(Mapper, 'mapper_configured', receive_mapper_configured)

    def after_configured():
        for k, v in mappers.items():
            logging.critical("%s = %s", k, v)

    listen(Mapper, 'after_configured', after_configured)
