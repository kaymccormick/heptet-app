from zope.interface import Interface


class IMapperInfo(Interface):
    def get_mapper_info(key):
        pass
