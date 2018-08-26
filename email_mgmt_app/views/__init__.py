from pyramid.request import Request

from email_mgmt_app.root import RootFactory
from email_mgmt_app.entity.view import BaseView
from pyramid.config import Configurator


class MainView(BaseView):
    pass

def includeme(config: Configurator):
    config.register_entry_point('_main')
    config.add_view(MainView, name='', renderer='templates/main_child.jinja2', context=RootFactory, entry_point_key='_main')
