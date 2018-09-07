import logging

logger = logging.getLogger(__name__)

def test_namespace_store(namespace_store):
    logger.critical("%s", namespace_store.namespace)
    assert namespace_store

def test_namespace_get_id(namespace_store):
    id = namespace_store.get_id()
    logger.critical("%s", id)
    assert id

