import logging
from unittest import TestCase

from res import Resource, RootResource

logger = logging.getLogger(__name__)

def test_resource_meta():
    root = RootResource()
    a = Resource(name='a', parent=root)
    b = Resource(name='b', parent=root)
    logger.warning("%s, %s", type(a), type(b))
    assert False

def test_root_Resource():
    root = RootResource()
    assert type(root) == RootResource
    assert False