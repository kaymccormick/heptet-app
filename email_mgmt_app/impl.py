from zope.interface import implementer

from email_mgmt_app.interfaces import IMapperInfo


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