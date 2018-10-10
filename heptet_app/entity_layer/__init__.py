from collections import MutableSequence
from typing import TypeVar

from zope.interface import Interface, implementer


class IEntityTypeContainer(Interface):
    pass


EntityType = TypeVar('EntityType')
@implementer(IEntityTypeContainer)
class EntityTypeContainer:

    def __init__(self):
        super().__init__()
        self._entity_types = [] # types.MutableSequence[EntityType]





def _add_entity_type(config, entity_type):
    etc = config.registry.getUtility(IEntityTypeContainer)
    etc.add_entity_type(entity_type)

    pass


def includeme(config):
    etc = EntityTypeContainer()
    config.registry.registerUtility(etc)
    config.add_directive('add_entity_type', _add_entity_type)
