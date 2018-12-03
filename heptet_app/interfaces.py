from zope.interface import Interface

class IResourceContext(Interface):
    pass

class IEntryPointFactory(Interface):
    pass


class IResourceRoot(Interface):
    """
    Interface marking the resource root.
    """
    pass


class IGeneratorContext(Interface):
    pass


class IEntryPointView(Interface):
    pass


class IProcess(Interface):
    pass


class IObject(Interface):
    pass


class IEntryPoint(IObject):
    pass


class ITemplateSource(Interface):
    pass


class ITemplate(Interface):
    pass


class ITemplateVariable(Interface):
    pass


class ICollector(Interface):
    pass


class IRelationshipSelect(Interface):
    pass


class INamespaceStore(Interface):
    pass


# does it make sense to use 'key' here? no
class IMapperInfo(Interface):
    pass


# @implementer(IInterface)
class IResource(Interface):
    """
    Interface for a resource, i.e. something which is in the resource tree.
    """
    pass


class IFormContext(Interface):
    pass


class IResourceManager(Interface):
    pass


class IEntryPointGenerator(Interface):
    pass


class IEntryPointMapperAdapter(Interface):
    pass


class IEntryPoints(Interface):
    pass

