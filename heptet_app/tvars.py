import collections
import logging
import typing
from collections import MutableMapping
from typing import Iterator, AnyStr

from marshmallow import Schema, fields

logger = logging.getLogger(__name__)
T = typing.TypeVar('T')


class TemplateVarSchema(Schema):
    value = fields.String(attribute='_value')


class TemplateVarsSchema(Schema):
    vars = fields.Dict(values=fields.Nested(TemplateVarSchema), keys=fields.String())


class TemplateVar(typing.Generic[T]):

    def __init__(self, initial_value: T = None) -> None:
        super().__init__()
        self._value = initial_value

    @property
    def value(self) -> T:
        return self._value

    @value.setter
    def value(self, new: T) -> None:
        self._value = new

    def __eq__(self, other):
        return self._value.__eq__(other)

    def __hash__(self):
        return self._value.__hash__()

    def __repr__(self):
        return self._value.__repr__()


class TemplateVars(MutableMapping):
    def __init__(self, **kwargs) -> None:
        super().__init__()
        # for name,tvar in kwargs.items():
        self.vars = {**kwargs}

    def __setitem__(self, k, v) -> None:
        if k in ('vars',):
            raise TypeError

        if isinstance(v, TemplateVar):
            self.vars[k] = v
        else:
            if isinstance(v, str):
                var = StringTemplateVar(v)
            elif hasattr(v, 'keys') and callable(v.keys):
                var = MappingTemplateVar(v)
            elif hasattr(v, 'insert'):
                var = MutableSequenceTemplateVar(v)
            else:
                var = TemplateVar[type(v)](v)
            self[k] = var

    def __delitem__(self, v) -> None:
        self.vars.__delitem__(v)

    def __len__(self) -> int:
        return self.vars.__len__()

    def __iter__(self) -> Iterator:
        return self.vars.__iter__()

    @property
    def schema(self):
        return self._schema

    # def __missing__(self, key):

    def __getitem__(self, key):
        # dont create a variable "vars" because it messes with serialziation
        if key in ('vars,'):
            raise TypeError

        if key not in self.vars:
            self.vars[key] = TemplateVar(key)
        return self.vars[key]

    def __contains__(self, o):
        return self.vars.__contains__(o)

    def __repr__(self):
        return self.vars.__repr__()

    def __str__(self):
        return self.vars.__str__()


class StringTemplateVar(TemplateVar[str]):
    def __init__(self, initial_value: AnyStr = "") -> None:
        super().__init__(initial_value)

    def __str__(self):
        return self.value

    def __len__(self):
        return self._value.__len__()

    def __getitem__(self, i):
        return self._value.__getitem__(i)

    def __setitem__(self, key, value):
        return self._value.__setitem__(key, value)


class MappingTemplateVar(TemplateVar[MutableMapping], collections.abc.MutableMapping):
    def __init__(self, initial_value: MutableMapping) -> None:
        super().__init__(initial_value)

    def __getitem__(self, k):
        return self._value.__getitem__(k)

    def __setitem__(self, k, v) -> None:
        self._value.__setitem__(k, v)

    def keys(self):
        return self._value.keys()

    def __iter__(self):
        return self._value.__iter__()

    def __len__(self):
        return self._value.__len__()

    def __delitem__(self, v) -> None:
        self._value.__delitem__(v)

    def __contains__(self, item):
        return self._value.__contains(item)


class MutableSequenceTemplateVar(TemplateVar[typing.MutableSequence], collections.abc.MutableSequence):
    def __init__(self, initial_value: typing.MutableSequence) -> None:
        super().__init__(initial_value)

    def __getitem__(self, i):
        return self.value.__getitem__(i)

    def __setitem__(self, i, o):
        self.value.__setitem__(i, o)

    def __delitem__(self, i):
        self.value.__delitem__(i)

    def __len__(self):
        return self.value.__len__()

    def insert(self, index, object):
        return self.value.insert(index, object)
