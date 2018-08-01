from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    ForeignKey, Sequence)
from sqlalchemy.orm import relationship

from .meta import Base, metadata


class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    value = Column(Integer)


sequence = Sequence('entity_id_seq', metadata=metadata)
class Entity(Base):
    __tablename__ = 'entity'
    id = Column(Integer, sequence, server_default=sequence.next_value(), primary_key=True)
    name = Column(Text)
    kind = Column(Text)
    person = relationship('Person', uselist=False, back_populates='entity')
    domains = relationship('Domain', back_populates='owner')


class Person(Base):
    __tablename__ = 'person'
    id = Column(Integer, ForeignKey('entity.id'), Sequence('entity_seq', metadata=metadata), primary_key=True)
    entity = relationship('Entity', uselist=False, back_populates='person')

class Domain(Base):
    __tablename__ = 'domain'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    owner_id = Column(Integer, ForeignKey('entity.id'))
    owner = relationship('Entity', back_populates='domains')

#Index('my_index', MyModel.name, unique=True, mysql_length=25)
