import logging
from unittest import TestCase

from res import Resource, RootResource

logger = logging.getLogger(__name__)

def test_resource_meta():
    root = RootResource()
    a = Resource(name='a', parent=root)
    b = Resource(name='b', parent=root)
    logger.warning("%s, %s", type(a), type(b))

def test_root_Resource():
    root = RootResource()
    root2 = RootResource()
    assert root is root2
    #assert type(root) == RootResource
