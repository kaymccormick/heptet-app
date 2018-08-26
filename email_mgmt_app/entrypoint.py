from typing import AnyStr


class EntryPoint:
    def __init__(self, key: AnyStr, js=None) -> None:
        self._key = key
        self._js = js

    def __json__(self, request):
        return self.key

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, new):
        self._key = new

    @property
    def js(self):
        return self._js

    @js.setter
    def js(self, new):
        self._js = new
