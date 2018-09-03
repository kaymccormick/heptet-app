import abc
from typing import AnyStr

from zope import interface

from zope.component import adapter
from zope.interface import implementer, Interface

from email_mgmt_app import MapperInfosMixin
from email_mgmt_app.impl import MapperWrapper

class IEntryPoints(Interface):
    def get_entry_points():
        pass
    def add_entry_point(entry_point):
        pass



@implementer(IEntryPoints)
class EntryPoints:
    def __init__(self) -> None:
        self._entry_points = []

    def get_entry_points(self):
        return self._entry_points

    def add_entry_point(self, entry_point):
        self._entry_points.append(entry_point)

class IEntryPoint(Interface):
    pass


@interface.implementer(IEntryPoint)
class EntryPoint:
    """

    """
    def __init__(self, key: AnyStr, js=None, view_kwargs: dict=None, mapper_wrapper: MapperWrapper=None) -> None:
        """

        :param key:
        :param js:
        :param view:
        """
        self._key = key
        self._js = js
        self._view_kwargs = view_kwargs
        self._view = None
        self._mapper_wrapper = mapper_wrapper

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


class EntryPointGenerator(MapperInfosMixin, metaclass=abc.ABCMeta):
    """

    """
    def __init__(self, entry_point: EntryPoint, request, logger=None) -> None:
        """

        :param entry_point:
        :param context:
        :param request:
        :param logger:
        """
        super().__init__()

        self._entry_point = entry_point
        # TODO we will need to handle more than a single mapper info
        # info = entry_point.operation.resource_manager.mapper_info
        # self._mapper_infos = {}
        # self._mapper_infos[info['mapper_key']] = info
        self._request = request

        self.logger = logger

    @property
    def entry_point(self) -> EntryPoint:
        return self._entry_point

    @abc.abstractmethod
    def js_stmts(self):
        pass

    @abc.abstractmethod
    def js_imports(self):
        pass

    @abc.abstractmethod
    def extra_js_stmts(self):
        pass

entry_points = EntryPoints()

def register_entry_point(config, entry_point: IEntryPoint):
    entry_points.add_entry_point(entry_point)
    config.registry.registerUtility(entry_point, IEntryPoint, entry_point.key)


def includeme(config: 'Configurator'):
    config.registry.registerUtility(EntryPoints())
    config.add_directive('register_entry_point', register_entry_point)

