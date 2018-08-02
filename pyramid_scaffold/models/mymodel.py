from typing import AnyStr

from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    ForeignKey, Sequence, event)
from sqlalchemy.orm import relationship

from .meta import Base, metadata

def entity_listener(target, value, oldvalue, initiator):
    value.kind = "domain"

sequence = Sequence('entity_id_seq', metadata=metadata)
class Entity(Base):
    __tablename__ = 'entity'
    id = Column(Integer, sequence, server_default=sequence.next_value(), primary_key=True)
    name = Column(Text)
    kind = Column(Text)
    owner_id = Column(Integer, ForeignKey('entity.id'))
    person = relationship('Person', uselist=False, back_populates='entity')
    domain = relationship('Domain', uselist=False, back_populates='entity', foreign_keys='[Domain.id]')
    host = relationship('Host', uselist=False, back_populates='entity')
    owned_entities = relationship('Entity', back_populates='owner', foreign_keys='[Entity.id]')
    owner = relationship('Entity', back_populates='owned_entities', foreign_keys='[Entity.owner_id]', remote_side=[id])

class Person(Base):
    __tablename__ = 'person'
    id = Column(Integer, ForeignKey('entity.id'), sequence, primary_key=True)
    entity = relationship('Entity', uselist=False, back_populates='person')

class Domain(Base):
    __tablename__ = 'domain'

    id = Column(Integer, ForeignKey('entity.id'), sequence, primary_key=True)
    entity = relationship('Entity', uselist=False, back_populates='domain', foreign_keys=[id])

    @property
    def name(self):
        if self.entity is not None and isinstance(self.entity, Entity):
            return self.entity.name
        return None

    @name.setter
    def name(self, name: AnyStr) -> None:
        assert self.entity is not None and isinstance(self.entity, Entity)
        self.entity.name = name

class Host(Base):
    __tablename__ = 'host'
    id = Column(Integer, ForeignKey('entity.id'), sequence, primary_key=True)
    entity = relationship('Entity', uselist=False, back_populates='host')

#Index('my_index', MyModel.name, unique=True, mysql_length=25)
event.listen(Domain.entity, 'set', entity_listener)

@event.listens_for(Domain, 'init')
def domain_init(target, args, kwargs):
    target.entity = Entity()
