from zope.interface import Interface

class INamespaceStore(Interface):
    def get_id(preferred, bits):
        pass
    def make_namespace(key, namespace):
        pass
    def get_namespace(key):
        pass


class IHtmlIdStore(Interface):
    def get_id(preferred, bits):
        pass
    def get_namespace(key, namespace):
        pass


# does it make sense to use 'key' here? no
class IMapperInfo(Interface):
    def get_mapper_info(key):
        pass
    def get_one_mapper_info():
        pass

