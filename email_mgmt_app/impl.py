import logging

from zope.interface import implementer

from email_mgmt_app.interfaces import IMapperInfo, IHtmlIdStore, INamespaceStore
from email_mgmt_app.exceptions import IdTaken

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


@implementer(INamespaceStore)
class IdStore:
    def __init__(self, name) -> None:
        self._namespace = {}
        self._name = name

    def get_namespace(self, key, namespace):
        logger.debug("in get_namespace(%s, %s)", key, namespace)
        assert key not in self._namespace
        self._namespace[key] = { 'key': key, 'namespace': namespace, 'items': {} }
        return key

    def set_namespace(self, key):
        assert key in self._namespace
        self._cur_namespace = key

    def get_id(self, preferred, bits):
        assert bits
        assert self._cur_namespace and self._cur_namespace in self._namespace
        items = self._namespace[self._cur_namespace]['items']
        assert preferred not in items
        items[preferred] = bits
        return self.make_global_id(self._cur_namespace, preferred)

    def make_global_id(self, namespace, id):
        global_id = "%s.%s" % (namespace, id)
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

