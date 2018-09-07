from typing import AnyStr

from pyramid.interfaces import IRequestFactory
from pyramid.request import Request

from email_mgmt_app.root import RootFactory
from email_mgmt_app.view import BaseView
from pyramid.config import Configurator

from email_mgmt_app.entrypoint import EntryPoint


class MainView(BaseView):
    pass


class MainEntryPoint(EntryPoint):
    def __init__(self, key: AnyStr='_main', registry=None) -> None:
        super().__init__(key=key, registry=registry)


def includeme(config: Configurator):
    main = MainEntryPoint(registry=config.registry)
    request = config.registry.queryUtility(IRequestFactory, default=Request)({})
    request.registry = config.registry
    #generator = MainView.entry_point_generator_factory()(main, request)
    #main.generator = generator
    config.register_entry_point(main)
    config.add_view(MainView, name='', renderer='templates/main_child.jinja2', context=RootFactory, entry_point=MainEntryPoint)
