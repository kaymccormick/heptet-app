from zope.interface.interfaces import IInterface

from zope.interface import Interface, implementer

class IGeneratorContext(Interface):
    pass

class IEntryPointView(Interface):
    pass

class IProcess(Interface):
    def process():
        pass


class ICollectorContext(Interface):
    def get_backing_var():
        pass


class IObject(Interface):
    pass


class IVariableType(Interface):
    pass


class IEntryPoint(IObject):
    def generate():
        pass

    def get_template_name():
        pass

    def set_template_name(template_name):
        pass

    def get_key():
        pass

    def get_output_filename():
        pass

    def set_output_filename(filename):
        pass


class ITemplateSource(Interface):
    def get_name():
        pass

    def render(**kwargs):
        pass


class ITemplate(Interface):
    def get_name():
        pass

    def get_content():
        pass

    def render(**kwargs):
        pass


class ITemplateVariable(Interface):
    def get_name():
        pass

    def get_value():
        pass


class ICollector(Interface):
    def collect(*args, **kwargs):
        pass


class IBuilder(Interface):
    pass

class IRelationshipSelect(Interface):
    def get_select():
        pass

    def set_context():
        pass


class INamespaceStore(Interface):
    pass


# does it make sense to use 'key' here? no
class IMapperInfo(Interface):
    def get_mapper_info(key):
        pass

    def get_one_mapper_info():
        pass


class ISqlAlchemySession(object):
    pass


# @implementer(IInterface)
class IResource(Interface):
    pass


class IFormContext(Interface):
    pass


class IRootResource(IResource):
    def get_data():
        pass

    def get_root_resource():
        pass


class IResourceManager(Interface):
    pass