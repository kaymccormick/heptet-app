from zope.interface import Interface


# does it make sense to use 'key' here? no
class IMapperInfo(Interface):
    def get_mapper_info(key):
        pass
    def get_one_mapper_info():
        pass

