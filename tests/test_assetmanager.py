import logging
from os import path

logger = logging.getLogger(__name__)


def test_assetmanager(make_asset_manager):
    dir = "test123"
    am = make_asset_manager(dir, False)
    assert am.output_dir
    assert dir == am.output_dir


def test_assetmanager_no_mkdir(make_asset_manager):
    dir = "test123"
    am = make_asset_manager(dir, False)
    assert am.output_dir
    assert dir == am.output_dir
    assert not path.exists(am.output_dir)


def test_assetmanager_open(asset_manager):
    # with patch(asset_manager.get, )

    pass
