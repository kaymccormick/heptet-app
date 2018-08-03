from typing import AnyStr

from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    ForeignKey, Sequence, event, ForeignKeyConstraint, String)
from sqlalchemy.orm import relationship

from .meta import Base, metadata

class Person(Base):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True)

class Domain(Base):
    __tablename__ = 'domain'

    id = Column(Integer, primary_key=True)
    name = Column(String)

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
