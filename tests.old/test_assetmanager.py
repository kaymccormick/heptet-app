import logging
from os import path
from pathlib import Path

import pytest

logger = logging.getLogger(__name__)


@pytest.fixture
def test_dir_fixture():
    import tempfile
    with tempfile.TemporaryDirectory() as dirname:
        yield dirname


def test_assetmanager(make_asset_manager, test_dir_fixture):
    dir = Path(test_dir_fixture)
    dir = dir.joinpath("noexist")
    am = make_asset_manager(dir, True)
    assert am.output_dir
    assert dir == am.output_dir
    assert path.exists(am.output_dir)


def test_assetmanager_no_mkdir(make_asset_manager, test_dir_fixture):
    dir = Path(test_dir_fixture)
    dir = dir.joinpath("noexist")
    am = make_asset_manager(dir, False)
    assert am.output_dir
    assert dir == am.output_dir
    assert not path.exists(am.output_dir)




@pytest.fixture(params=[('test1', 'test2')])
def disc_fixture(request):
    return tuple(request.param)


