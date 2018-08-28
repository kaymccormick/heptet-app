import logging
from dataclasses import dataclass
from typing import AnyStr, Sequence, Mapping, MutableSequence, Dict, List

from sqlalchemy import Table, Column
from sqlalchemy.orm import Mapper, RelationshipProperty

from email_mgmt_app.info import TableInfo, ColumnInfo, InfoBase, TypeInfo, MapperInfo, RelationshipInfo, \
    LocalRemotePairInfo, PairInfo

logger = logging.getLogger(__name__)


class IAdapter:
    pass


@dataclass
class AlchemyInfo(InfoBase):
    tables: dict = None
    mappers: dict = None


class AlchemyAdapter(IAdapter):
    def __init__(self) -> None:
        self._info = AlchemyInfo(tables={}, mappers={})
        pass

    @property
    def info(self) -> AlchemyInfo:
        return self._info

    @info.setter
    def info(self, new: AlchemyInfo) -> None:
        self._info = new

    def process_table(self, table_name: AnyStr, table: Table) -> TableInfo:
        assert table_name == table.name
        i = TableInfo(name=table.name, key=table.key,
                      columns=[], primary_key=[]
                      )
        self.info.tables[table_name] = i

        primary_key = table.primary_key
        for key_col in primary_key:
            i.primary_key.append(key_col.key)

        col: Column
        for col in table.columns:
            _i = ColumnInfo(name=col.name, key=col.key)
            i.columns.append(_i)

        return i

    def process_mapper(self, mapper_key, mapper: Mapper):
        """

        :param mapper:
        :return:
        """

        mapped_table = mapper.mapped_table  # type: Table

        primary_key = []
        for pkey in mapper.primary_key:
            primary_key.append([pkey.table.key, pkey.key])

        columns = []
        col: Column
        for col in mapper.columns:
            coltyp = col.type
            t = col.table  # type: Table
            i = ColumnInfo(key=col.key, compiled=str(col.compile()),
                           table=t.name,
                           type=TypeInfo(compiled=str(col.type.compile())), )

            columns.append(i)

        relationships = []
        for relationship in mapper.relationships:
            relationships.append(self.process_relationship(relationship))

        mi = MapperInfo(columns=columns,
                        relationships=relationships,
                        primary_key=primary_key,
                        mapped_table=mapped_table.key)
        self.info.mappers[mapper_key] = mi

        return mi

    # desc: InspectionAttr
    # for desc in mapper.all_orm_descriptors:
    #     logging.critical("[%s] = %s", str(desc), type(desc))
    #     if desc.is_attribute:
    #         process_attribute(desc)
    #         logging.critical("%s is attribute", desc)
    #     if desc.is_property:
    #         assert False
    #
    def process_relationship(self, rel: RelationshipProperty):
        y = rel.argument
        if callable(y):
            z = y()
        else:
            z = y.entity

        pairs = []
        for pair in rel.local_remote_pairs:
            pairs.append(LocalRemotePairInfo(local=PairInfo(table=pair[0].table.name, column=pair[0].name),
                                             remote=PairInfo(table=pair[1].table.name, column=pair[1].name))
                         )
            secondary = None
            if rel.secondary:
                secondary = rel.secondary.name
            if rel.backref and not isinstance(rel.backref, str):
                print(rel.backref)

            i = RelationshipInfo(local_remote_pairs=pairs, argument=[z.__module__, z.__name__],
                                 key=rel.key,
                                 secondary=secondary, backref=rel.backref,
                                 direction=rel.direction.name,
                                 )
        return i
