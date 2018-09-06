from zope.interface import Interface


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


class IFormRepresentationBuilder(Interface):
    def form_representation(context):
        pass


class IRelationshipSelect(Interface):
    def get_select():
        pass

    def set_context():
        pass


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


class ISqlAlchemySession(object):
    pass


class IResource(Interface):
    pass