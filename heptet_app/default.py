from heptet_app import EntryPoint, ResourceManager
# this is crufty and should go away


class DefaultEntryPoint(EntryPoint):

    def __init__(self, resource_manager=None):
        key = "_default"

        super().__init__(key, resource_manager)


class DefaultResourceManager(ResourceManager):
    def __init__(self):
        super().__init__('_default', '_default', None, '_default', None)


_default_manager = DefaultResourceManager()
_default_entry_point = DefaultEntryPoint(_default_manager)


def default_entry_point():
    return _default_entry_point


def default_manager():
    return _default_manager