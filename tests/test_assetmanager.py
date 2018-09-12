from process import AssetManager
import logging

logger = logging.getLogger(__name__)

def test_assetmanager(asset_manager):
    logger.critical("%r", asset_manager)

def test_assetmanager_open(asset_manager):
    pass
