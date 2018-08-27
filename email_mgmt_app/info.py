from dataclasses import dataclass
from typing import AnyStr, Sequence, MutableSequence
from dataclasses_json import DataClassJsonMixin
from sqlalchemy.orm import RelationshipProperty


class InfoBase(DataClassJsonMixin):
    def __json__(self):
        return self.__dict__
    pass

class Mixin:
    pass

@dataclass
class KeyMixin:
    key: str=None

@dataclass
class CompiledMixin:
    compiled: str=None

@dataclass
class PairInfo(Mixin, InfoBase):
    table: AnyStr=None
    column: AnyStr=None

@dataclass
class LocalRemotePairInfo(Mixin, InfoBase):
    local: PairInfo=None
    remote: PairInfo=None

@dataclass
class RelationshipInfo(Mixin, InfoBase):
    argument: object=None
    secondary: object=None
    backref: AnyStr=None
    local_remote_pairs: Sequence[LocalRemotePairInfo]=None
    pass

@dataclass
class ColumnInfo(KeyMixin, CompiledMixin, Mixin, InfoBase):
    type: 'TypeInfo'=None
    table: AnyStr=None
    name: AnyStr=None
    pass



@dataclass
class MapperInfo(Mixin, InfoBase):
    columns: MutableSequence[ColumnInfo]=None
    relationships: MutableSequence[RelationshipInfo]=None
    pass

@dataclass
class TypeInfo(CompiledMixin, Mixin, InfoBase):
    pass


@dataclass
class TableInfo(KeyMixin, Mixin, InfoBase):
    name: AnyStr=None
    primary_key: Sequence[AnyStr]=None
    columns: Sequence[ColumnInfo]=None
    pass

@dataclass
class InfoContainer(Mixin, InfoBase):
    mappers: Sequence[MapperInfo] = None
    tables: Sequence[TableInfo] = None


