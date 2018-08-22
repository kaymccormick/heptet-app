from pyramid.request import Request

from email_mgmt_app.root import RootFactory
from email_mgmt_app.entity.view import BaseView
from pyramid.config import Configurator


class MainView(BaseView):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)


def includeme(config: Configurator):
    config.add_view('.MainView', name='', renderer='templates/main_child.jinja2', context=RootFactory)
