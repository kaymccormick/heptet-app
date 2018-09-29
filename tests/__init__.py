import logging
from typing import TypeVar, Generic
from unittest.mock import MagicMock, PropertyMock
import json

from pyramid.registry import Registry

logger = logging.getLogger(__name__)
T = TypeVar('T')


class AbstractProperty(Generic[T]):
    def __init__(self):
        pass


class Property(AbstractProperty[T]):
    def __init__(self, obj, name, init_value: T = None, wraps=None) -> None:
        super().__init__()
        self._obj = obj
        self._name = name
        self._value = init_value
        # self._wraps = wraps

    def __get__(self, instance, owner) -> T:
        assert self is instance
        # if self._wraps:
        #     return self._wraps.__get__(instance, owner)
        return self._value

    def __set__(self, instance, value: T):
        assert self is instance
        self._value = value
        setattr(self._obj, self._name, value)

    def __call__(self, *args):
        if args:
            self._value = args[0]
            setattr(self._obj, self._name, args[0])
        else:
            return self._value


def dump_mock_calls(mock, calls):
    logger.critical("Mock: %r", mock)
    if calls:
        logger.critical("Calls:")
        i = 0
        for call in calls:
            logger.critical("    [%02d] %r", i, call)
            i = i + 1

    else:
        logger.critical("No calls.")


def mock_wrap_config(config, registry):
    class RegistryMock(MagicMock):
        pass

    class ConfigMock(MagicMock):
        def __init__(self, *args, **kw):
            super().__init__(*args, **kw)
            #type(self).registry = PropertyMock(return_value=registry)

        def _get_child_mock(self, **kw):
            logger.critical("kw =%r", kw)
            if kw['name'] == 'registry':
                logger.critical("kw is %r", kw)
                kw['spec'] = Registry
                registry_mock = RegistryMock(**kw)
                return registry_mock
            return super()._get_child_mock(**kw)

    mock = ConfigMock(spec=config, wraps=config)
    return mock
