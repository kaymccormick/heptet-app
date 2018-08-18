from typing import AnyStr, Callable, Dict, NewType


class Resource():
    pass


class ContainerResource(Dict[AnyStr, Resource], Resource):
    def __init__(self, dictinit) -> None:
        super().__init__(dictinit)



class LeafResource(Resource):
    def __getattr__(self, item):
        raise KeyError


class EntityResource():
    def __init__(self, name, entity_type) -> None:
        super().__init__()
        self._name = name
        self._entity_type = entity_type

    @property
    def entity_name(self):
        return self._name

class NodeNamePredicate():

    def __init__(self, val, config) -> None:
        self._val = val
        self._config = config

    def text(self):
        return 'node_name = %s' % (self._val)

    phash = text

    def __call__(self, context, request):
        if isinstance(context, ResourceRegistration) and context.node_name == self._val:
            return True
        return False


class ResourceRegistration():
    def __init__(self, name: AnyStr, view=None, callable: Callable=None, node_name: AnyStr=None, entity_type=None) -> None:
        super().__init__()
        self._name = name
        self._callable = callable
        if node_name is None:
            node_name = name
        self._node_name = node_name
        self._entity_type = entity_type
        self._view = view

    @property
    def callable(self):
        return self._callable

    @property
    def name(self):
        return self._name

    @property
    def node_name(self):
        return self._node_name