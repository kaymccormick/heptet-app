from pyramid.config import Configurator
from sqlalchemy import Integer

from email_mgmt_app.entity.view import BaseView
from email_mgmt_app.res import ResourceRegistration, ResourceManager, Resource, OperationArgument


class DbView(BaseView):
    def __call__(self, *args, **kwargs):
        return {}


def includeme(config: Configurator):
    registration = ResourceManager.reg('db', default_view=DbView)
    mgr = ResourceManager(config, registration)
    mgr.operation('view', DbView, [], renderer="templates/db/view.jinja2")

    config.add_resource_manager(mgr)
    #config.add_view(".DbView", name='view', context=Resource,
