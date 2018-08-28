import abc
from typing import AnyStr

from email_mgmt_app.info import MapperInfosMixin


class EntryPoint:
    """

    """
    def __init__(self, key: AnyStr, js=None, view_kwargs: dict=None, operation: 'ResourceOperation'=None) -> None:
        """

        :param key:
        :param js:
        :param view:
        """
        self._key = key
        self._js = js
        self._view_kwargs = view_kwargs
        self._view = None
        self._operation = operation

    def __str__(self):
        return repr(self.__dict__)

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

    @property
    def view_kwargs(self) -> dict:
        return self._view_kwargs

    @view_kwargs.setter
    def view_kwargs(self, new: dict):
        self._view_kwargs = new

    @property
    def view(self):
        return self._view

    @view.setter
    def view(self, new):
        self._view = new

    @property
    def operation(self) -> 'ResourceOperation':
        return self._operation


class EntryPointGenerator(MapperInfosMixin, metaclass=abc.ABCMeta):
    def __init__(self, ep: EntryPoint, context, request) -> None:
        super().__init__()
        self._context = context
        self._request = request
        self._mapper_infos = {}
        self._entry_point = ep
        info = ep.operation.resource_manager.mapper_info
        self._mapper_infos[info['mapper_key']] = info

    @property
    def entry_point(self) -> EntryPoint:
        return self._entry_point

    @abc.abstractmethod
    def js_stmts(self):
        pass

    @abc.abstractmethod
    def js_imports(self):
        pass





