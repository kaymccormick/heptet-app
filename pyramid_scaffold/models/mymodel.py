from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    ForeignKey, Sequence)
from sqlalchemy.orm import relationship

from .meta import Base, metadata

sequence = Sequence('entity_id_seq', metadata=metadata)
class Entity(Base):
    __tablename__ = 'entity'
    id = Column(Integer, sequence, server_default=sequence.next_value(), primary_key=True)
    name = Column(Text)
    kind = Column(Text)
    person = relationship('Person', uselist=False, back_populates='entity')
    host = relationship('Host', uselist=False, back_populates='entity')
    domains = relationship('Domain', back_populates='owner')


class Person(Base):
    __tablename__ = 'person'
    id = Column(Integer, ForeignKey('entity.id'), sequence, primary_key=True)
    entity = relationship('Entity', uselist=False, back_populates='person')

class Domain(Base):
    __tablename__ = 'domain'
    id = Column(Integer, sequence, primary_key=True)
    name = Column(Text)
    owner_id = Column(Integer, ForeignKey('entity.id'))
    owner = relationship('Entity', back_populates='domains')

class Host(Base):
    __tablename__ = 'host'
    id = Column(Integer, ForeignKey('entity.id'), sequence, primary_key=True)
    entity = relationship('Entity', uselist=False, back_populates='host')

#Index('my_index', MyModel.name, unique=True, mysql_length=25)
