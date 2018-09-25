from typing import TypeVar, Generic

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
