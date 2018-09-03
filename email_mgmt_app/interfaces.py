from zope.interface import Interface


class IMapperInfo(Interface):
    def get_mapper_info(key):
        pass
    def get_one_mapper_info():
        pass

