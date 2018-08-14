import zope

from sqlalchemy import Column, Integer, String, Float, ForeignKey, engine_from_config
from sqlalchemy.orm import relationship, configure_mappers, sessionmaker

from email_mgmt_app.entity.model.meta import Base



class Mixin(object):
    pass


class Person(Mixin, Base):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True)


class Domain(Base):
    __tablename__ = 'domain'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __json__(self, request):
        return { 'id': self.id, 'name': self.name }


class ServiceEntry(Base):
    __tablename__ = 'service_entry'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    port_num = Column(Integer)
    protocol_name = Column(String)
    weight = Column(Float, default=0)
    description = Column(String, default="")


class Host(Base):
    __tablename__ = 'host'
    id = Column(Integer, primary_key=True)

    name = Column(String)
    domain_id = Column(Integer, ForeignKey('domain.id'))
    domain = relationship('Domain', backref='hosts')


class EmailAddress(Base):
    __tablename__ = 'email_address'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    host_id = Column(Integer, ForeignKey('host.id'))
    host = relationship('Host', backref='email_addresses')

configure_mappers()


def get_engine(settings, prefix='sqlalchemy.'):
    return engine_from_config(settings, prefix)


def get_session_factory(engine):
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory


def get_tm_session(session_factory, transaction_manager):
    """
    Get a ``sqlalchemy.orm.Session`` instance backed by a transaction.

    This function will hook the session to the transaction manager which
    will take care of committing any changes.

    - When using pyramid_tm it will automatically be committed or aborted
      depending on whether an exception is raised.

    - When using scripts you should wrap the session in a manager yourself.
      For example::

          import transaction

          engine = get_engine(settings)
          session_factory = get_session_factory(engine)
          with transaction.manager:
              dbsession = get_tm_session(session_factory, transaction.manager)

    """
    dbsession = session_factory()
    zope.sqlalchemy.register(
        dbsession, transaction_manager=transaction_manager)
    return dbsession


def includeme(config):
    """
    Initialize the model for a Pyramid app.

    Activate this setup using ``config.include('email_mgmt_app.models')``.

    """
    settings = config.get_settings()
    settings['tm.manager_hook'] = 'pyramid_tm.explicit_manager'

    # use pyramid_tm to hook the transaction lifecycle to the request
    config.include('pyramid_tm')

    # use pyramid_retry to retry a request when transient exceptions occur
    config.include('pyramid_retry')

    session_factory = get_session_factory(get_engine(settings))
    config.registry['dbsession_factory'] = session_factory

    # make request.dbsession available for use in Pyramid
    config.add_request_method(
        # r.tm is the transaction manager used by pyramid_tm
        lambda r: get_tm_session(session_factory, r.tm),
        'dbsession',
        reify=True
    )
