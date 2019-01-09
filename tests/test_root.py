from heptet_app import _get_root
from unittest.mock import MagicMock

def test_root_1():
    cb = MagicMock(name='on_create_cb')
    root = _get_root(cb)
    assert root is not None
    
