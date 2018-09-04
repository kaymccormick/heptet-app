import logging

from zope.interface import implementer

from email_mgmt_app.interfaces import IMapperInfo, IHtmlIdStore, INamespaceStore
from email_mgmt_app.exceptions import IdTaken, NamespaceCollision

logger = logging.getLogger(__name__)

@implementer(IMapperInfo)
class MapperWrapper:
    def __init__(self, mapper_info) -> None:
        self.mapper_info = mapper_info

    def get_mapper_info(self, key):
        assert key == self.mapper_info.local_table.key
        return self.mapper_info

    def get_one_mapper_info(self):
        return self.mapper_info

    @property
    def key(self):
        return self.mapper_info.local_table.key


class NamespaceEntry:
    def __init__(self, namespace_id) -> None:
        self._namespace_id = namespace_id

    def __str__(self):
        return str(self._namespace_id)


@implementer(INamespaceStore)
class NamespaceStore:
    def __init__(self, name) -> None:
        self._namespace = {}
        self._name = name

    def get_namespace(self, key, namespace):
        logger.debug("in get_namespace(%s, %s)", key, namespace)
        if key in self._namespace:
            raise NamespaceCollision(key, namespace, self._namespace[key])

        self._namespace[key] = { 'key': key, 'namespace': namespace, 'items': {} }
        return NamespaceEntry(key)

    def set_namespace(self, key):
        if isinstance(key, NamespaceEntry):
            key = key._namespace_id

        assert key in self._namespace
        self._cur_namespace = key

    def get_id(self, preferred, bits):
        assert bits
        assert self._cur_namespace and self._cur_namespace in self._namespace
        items = self._namespace[self._cur_namespace]['items']
        o = preferred
        i = 1
        while preferred in items:
            i = i + 1
            preferred = "%s%d" % (o, i)
            logger.debug("OMG trying %s", preferred)

        items[preferred] = bits
        return self.make_global_id(self._cur_namespace, preferred)

    def make_global_id(self, namespace, id):
        global_id = "0.%s.%s" % (namespace, id)
        return global_id




@implementer(IHtmlIdStore)
class HtmlIdStore:
    def __init__(self):
        self._ids = {}
        self._namespace = {}


    def get_id(self, preferred, bits):
        assert bits
        if preferred not in self._ids:
            self._ids[preferred] = bits
            return preferred

        raise IdTaken(preferred, self._ids)
        # else:
        #     assert False
        #     logger.debug("uh oh! preferred id %s taken", preferred)
        #     test = '.'.join(bits)
        #     import re
        #     test = re.sub('[^A-Za-z\._]', '_', test)
        #     logger.debug("going to use %s", test)
        #     return test

