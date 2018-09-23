from unittest.mock import MagicMock, PropertyMock

import pytest

from db_dump import RelationshipInfo


@pytest.fixture
def mock_relationship_info(local_remote_pair_info_mock):
    mock = MagicMock(RelationshipInfo)
    type(mock).local_remote_pairs = PropertyMock(return_value=[local_remote_pair_info_mock])
    return mock