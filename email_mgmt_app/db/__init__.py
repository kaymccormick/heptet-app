import logging

import pyramid_tm
import sqlalchemy
import stringcase
from pyramid.config import Configurator
from pyramid.util import DottedNameResolver
from sqlalchemy import Column, String
from sqlalchemy.orm import Session, Mapper

import email_mgmt_app
from email_mgmt_app.entity import Base, EntityView, EntityFormView
from email_mgmt_app.entity.model.email_mgmt import get_tm_session, get_session_factory, get_engine, AssociationTableMixin
from email_mgmt_app.res import ResourceManager, OperationArgument, ArgumentGetter


class MapperAdapter:
    pass


class DbAdapter:
    def __init__(self) -> None:
        self._cache = {}

    def manager(self, config=None, name=None, title=None, entity_type=None, inspect=None, node_name=None):
        """"""
        assert False
        mgr = ResourceManager(config=config, name=name, title=title, entity_type=entity_type, inspect=inspect, node_name=node_name)
        return mgr

    def get_db_session(self, config: Configurator):
        settings = config.get_settings()
        factory = get_session_factory(get_engine(settings))
        return get_tm_session(factory, pyramid_tm.explicit_manager(None))

    def add_action(self, config):
        session = self.get_db_session(config)
        self.populate(session, config)
        for key, val in self._cache.items():
            inspect = val # type: Mapper

            pkey = inspect.primary_key
            pkey_args = []
            pkey_col: Column
            for pkey_col in pkey:
                logging.info("pkey_col: %s", repr(pkey_col.key))
                pkey_args.append(OperationArgument(pkey_col.key, pkey_col.type, label=pkey_col.key.upper(), getter=ArgumentGetter()))

            manager = self.manager(config=config, name=key, title=stringcase.sentencecase(key),
                                   entity_type=inspect.entity, inspect=inspect, node_name=key)
            manager.operation('view', EntityView, pkey_args)
            manager.operation('form', EntityFormView, [OperationArgument.SubpathArgument('action', String, default='create')])
            config.add_resource_manager(manager)
            # was this
#            manager.add_action(config)

    def populate(self, session: Session, config: Configurator):
        #logging.warning("reg = %s", config.registry.email_mgmt_app)
        for x,y in config.registry.email_mgmt_app.mappers.items():
            # better way to do this for sure
            #logging.warning("got (%s, %s)", x, y)
            self._cache[x] = y

    def handle_mapping_inspect(self, model_class, result: Mapper):
        return
        assert result.configured
        name = model_class.__name__
        logging.info("handle_mapping_inspect(%s, )", name)
        table = result.local_table
        pkey = result.primary_key
        pkey_args = []
        pkey_col: Column
        for pkey_col in pkey:
            logging.info("pkey_col: %s", repr(pkey_col.key))
            pkey_args.append(OperationArgument(pkey_col.key, pkey_col.type, label=pkey_col.key.upper()))

        logging.info("args: %s", repr(pkey_args))
        #logging.info("%s", str(result))
        for element in result.iterate_properties:
#             if isinstance(element, RelationshipProperty):
# #                logging.info("rel = %s", repr(element.foreign_keys))
#             else:
#                 pass
            logging.info("elem: %s", repr(element))


resolver = DottedNameResolver(None)

def includeme(config: Configurator):

#    mgr = ResourceManager(config, name='db', title='db')
#    mgr.operation('view', DbView, [], renderer="templates/db/view.jinja2")

    settings = config.get_settings()
    factory = get_session_factory(get_engine(settings))
    session = get_tm_session(factory, pyramid_tm.explicit_manager(None))

    #adapter = DbAdapter()
    #add_db_adapter(config, adapter)


def add_db_adapter(config: Configurator, adapter: DbAdapter):
    config.action(adapter.add_action(config))
