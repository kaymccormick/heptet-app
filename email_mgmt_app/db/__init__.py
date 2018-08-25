import logging

import pyramid_tm
import sqlalchemy
import stringcase
import transaction
from pyramid.config import Configurator
from pyramid.util import DottedNameResolver
from sqlalchemy import Integer, Column, String
from sqlalchemy.orm import Session, RelationshipProperty, Mapper

import email_mgmt_app
from email_mgmt_app.entity.view import BaseView
from email_mgmt_app.res import ResourceRegistration, ResourceManager, Resource, OperationArgument
from email_mgmt_app.entity import Base, EntityView, EntityFormView
from email_mgmt_app.entity.model.email_mgmt import get_tm_session, get_session_factory, get_engine, AssociationMixin
from email_mgmt_app.res import SubpathArgumentGetter


class DbView(BaseView):

    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        d = self._response_dict
        dbsession = self.request.dbsession # type: Session
        inspect = sqlalchemy.inspection.inspect(dbsession.get_bind())
        logging.warning("inspect = %s", inspect)

        o = {}
        for x,y in email_mgmt_app.entity.model.email_mgmt.__dict__.items():
            try:
                if y != Base and issubclass(y, Base):
                    n = sqlalchemy.inspection.inspect(y)
                    o[x] = [y,n]
            except:
                pass


        d['o'] = o
        return d


class DbAdapter:
    def __init__(self) -> None:
        self._cache = {}

    def manager(self, config=None, name=None, title=None,
                                   entity_type=None, inspect=None, node_name=None):
        mgr = ResourceManager(config=config, name=name, title=title, entity_type=entity_type, inspect=inspect, node_name=node_name)
        return mgr

    def add_action(self, config):

        settings = config.get_settings()
        factory = get_session_factory(get_engine(settings))
        session = get_tm_session(factory, pyramid_tm.explicit_manager(None))

#        adapter = DbAdapter()

        self.populate(session)
        for key, val in self._cache.items():
            class_ = val[0]
            inspect = val[1] # type: Mapper

            pkey = inspect.primary_key
            pkey_args = []
            pkey_col: Column
            for pkey_col in pkey:
                logging.info("pkey_col: %s", repr(pkey_col.key))
                pkey_args.append(OperationArgument(pkey_col.key, pkey_col.type, label=pkey_col.key.upper()))

            manager = self.manager(config=config, name=key, title=stringcase.sentencecase(key),
                                   entity_type=class_, inspect=inspect, node_name=key)
            manager.operation('view', EntityView, pkey_args)
            manager.operation('form', EntityFormView, [OperationArgument.SubpathArgument('action', String, default='create')])

            manager.add_action(config)

    def populate(self, session: Session):
        for x,y in email_mgmt_app.entity.model.email_mgmt.__dict__.items():
            # better way to do this for sure
            try:
                if y != Base and issubclass(y, Base) and not issubclass(y, AssociationMixin):
                    n = sqlalchemy.inspection.inspect(y)
                    self.handle_mapping_inspect(y, n)
                    self._cache[x] = [y,n]
            except(TypeError):
                pass
        pass

    def handle_mapping_inspect(self, model_class, result: Mapper):
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

    mgr = ResourceManager(config, name='db', title='db')
    mgr.operation('view', DbView, [], renderer="templates/db/view.jinja2")

    settings = config.get_settings()
    factory = get_session_factory(get_engine(settings))
    session = get_tm_session(factory, pyramid_tm.explicit_manager(None))

    adapter = DbAdapter()


    add_db_adapter(config, adapter)
    config.add_resource_manager(mgr)
    #config.add_view(".DbView", name='view', context=Resource,


def add_db_adapter(config: Configurator, adapter: DbAdapter):
    config.action(adapter.add_action(config))
