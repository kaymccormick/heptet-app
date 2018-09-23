from unittest.mock import MagicMock, patch, call
import logging
from email_mgmt_app.process import FileAsset

logger = logging.getLogger(__name__)


def test_fileasset_init():
    obj = MagicMock()
    asset = FileAsset(obj, "test.out")
    assert asset

def test_fileasset_open():
    def my_open(asset, mode='r', buffering=-1, encoding=None,
             errors=None, newline=None):
        pass

    mock = MagicMock()
    with patch("email_mgmt_app.process.FileAsset.open", mock):

        obj = MagicMock()
        asset = FileAsset(obj, "test.out")
        with asset.open('w') as f:
            f.write('test')

        mock.assert_has_calls([call().__enter__().write('test')])


