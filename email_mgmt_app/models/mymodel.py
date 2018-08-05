from typing import AnyStr

from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    ForeignKey, Sequence, event, ForeignKeyConstraint, String, Boolean, Float)
from sqlalchemy.orm import relationship

from .meta import Base, metadata

class Person(Base):
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
