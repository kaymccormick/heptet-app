from unittest.mock import MagicMock, PropertyMock

import pytest

from db_dump import RelationshipInfo, LocalRemotePairInfo, TableColumnSpecInfo


@pytest.fixture
def local_remote_pair_info_mock():
    m = MagicMock(LocalRemotePairInfo)
    local = MagicMock(TableColumnSpecInfo)
    type(m).local = local
    remote = MagicMock(TableColumnSpecInfo)
    type(m).remote = remote
    m.__iter__.return_value = [local, remote]
    return m

@pytest.fixture
def mock_relationship_info(local_remote_pair_info_mock):
    mock = MagicMock(RelationshipInfo)
    type(mock).local_remote_pairs = PropertyMock(return_value=[local_remote_pair_info_mock])
    return mock