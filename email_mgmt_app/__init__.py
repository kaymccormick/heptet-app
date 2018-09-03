# package
from typing import AnyStr

from db_dump.info import MapperInfo

class MapperInfosMixin:
    @property
    def mapper_infos(self) -> dict:
        return self._mapper_infos

    def get_mapper_info(self, mapper_key: AnyStr) -> MapperInfo:
        assert mapper_key in self.mapper_infos
        return self.mapper_infos[mapper_key]

    def set_mapper_info(self, mapper_key: AnyStr, mapper_info: MapperInfo) -> None:
        self.mapper_infos[mapper_key] = mapper_info
