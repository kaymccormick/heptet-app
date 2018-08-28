from dataclasses import dataclass
from typing import AnyStr, Sequence, MutableSequence, List, Tuple, Dict
from dataclasses_json import DataClassJsonMixin
from sqlalchemy import Integer
from sqlalchemy.orm import RelationshipProperty

@dataclass
class InfoBase(DataClassJsonMixin):
    doc: AnyStr=None

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
class RelationshipInfo(KeyMixin, Mixin, InfoBase):
    argument: object=None
    mapper_key: AnyStr=None
    secondary: object=None
    backref: AnyStr=None
    local_remote_pairs: Sequence[LocalRemotePairInfo]=None
    direction: AnyStr=None
    pass

@dataclass
class ColumnInfo(KeyMixin, CompiledMixin, Mixin, InfoBase):
    type_: 'TypeInfo'=None
    table: AnyStr=None
    name: AnyStr=None
    pass



@dataclass
class MapperInfo(Mixin, InfoBase):
    mapper_key: AnyStr=None
    primary_key: Sequence[Tuple[AnyStr, AnyStr]]=None
    columns: MutableSequence[ColumnInfo]=None
    column_map: Dict[AnyStr, Integer]=None
    relationships: MutableSequence[RelationshipInfo]=None
    mapped_table: AnyStr=None
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


class MapperInfosMixin:
    @property
    def mapper_infos(self) -> dict:
        return self._mapper_infos

    def get_mapper_info(self, mapper_key: AnyStr) -> MapperInfo:
        assert mapper_key in self.mapper_infos
        return self.mapper_infos[mapper_key]

    def set_mapper_info(self, mapper_key: AnyStr, mapper_info: MapperInfo) -> None:
        self.mapper_infos[mapper_key] = mapper_info


