# package
import logging


# class MapperInfosMixin:
#     @property
#     def mapper_infos(self) -> dict:
#         return self._mapper_infos
#
#     def get_mapper_info(self, mapper_key: AnyStr) -> MapperInfo:
#         assert mapper_key in self.mapper_infos
#         return self.mapper_infos[mapper_key]
#
#     def set_mapper_info(self, mapper_key: AnyStr, mapper_info: MapperInfo) -> None:
#         self.mapper_infos[mapper_key] = mapper_info


class ArgumentContext:
    def __init__(self) -> None:
        self._subpath_index = 0

    @property
    def subpath_index(self):
        return self._subpath_index

    @subpath_index.setter
    def subpath_index(self, new):
        logging.info("setting subpath_index to %s", new)
        self._subpath_index = new

