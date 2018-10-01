from unittest.mock import MagicMock, PropertyMock

import pytest


@pytest.fixture
def make_relationship_info():
    def _make_relationship_info(**kwargs):
        return RelationshipInfo(**kwargs)

    return _make_relationship_info


@pytest.fixture
def local_remote_pair_info_mock():
    m = MagicMock(LocalRemotePairInfo)
    local = MagicMock(TableColumnSpecInfo, wraps=TableColumnSpecInfo(table='table1', column='child_id'))
    type(local).table = PropertyMock(return_value='table1')
    type(local).column = PropertyMock(return_value='child_id')

    type(m).local = local
    remote = MagicMock(TableColumnSpecInfo)
    type(m).remote = remote
    m.__iter__.return_value = [local, remote]
    return m


@pytest.fixture
def mapper_info_mock(local_remote_pair_info_mock):
    top_mock = MagicMock(MapperInfo, name='mapper_info')

    type(top_mock).entity = PropertyMock()

    col_info_mock = MagicMock(ColumnInfo, name='col_info')
    type(col_info_mock).key = PropertyMock(name='key', return_value='child_id')
    type(col_info_mock).name = PropertyMock(name='name', return_value='child_id')
    type(col_info_mock).table = PropertyMock(name='table', return_value='table1')
    type(col_info_mock).__visit_name__ = PropertyMock(return_value='column')
    type_mock = MagicMock(name='type')

    type(col_info_mock).type = PropertyMock(name='type', return_value=type_mock)

    # type(m).type = PropertyMock(return_value=TypeInfo())
    type(top_mock).columns = PropertyMock(list, return_value=[col_info_mock])

    class LocalTableMock(MagicMock):
        pass

    magic_mock = MagicMock(name='local_table')
    type(magic_mock).key = PropertyMock(name='key', return_value='table1')
    property_mock = PropertyMock(TableInfo, return_value=magic_mock)
    type(top_mock).local_table = property_mock

    rel_mock = MagicMock(RelationshipInfo, name='relationship_info')
    type(rel_mock).key = PropertyMock(return_value='key1')
    pair_mock = local_remote_pair_info_mock
    type(rel_mock).local_remote_pairs = PropertyMock(list, return_value=[pair_mock])
    type(rel_mock).direction = PropertyMock(return_value='MANYTOONE')
    type(rel_mock).argument = PropertyMock()
    type(rel_mock).secondary = PropertyMock(return_value=None)
    type(rel_mock).mapper = PropertyMock()

    rel_prop_mock = PropertyMock(list, name='relationships', return_value=[rel_mock])
    type(top_mock).relationships = rel_prop_mock

    # mock.local_table.key.side_effect = 'table1x'
    return top_mock