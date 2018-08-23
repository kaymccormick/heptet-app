from pyramid.config import Configurator

from ..entity.view import BaseView
from ..res import ResourceRegistration, ResourceManager, Resource


class DbView(BaseView):
    def __call__(self, *args, **kwargs):
        return {}


def includeme(config: Configurator):
    registration = ResourceRegistration('db', view=DbView)
    mgr = ResourceManager(config, registration)
    mgr.operation('view', DbView, renderer="templates/db/view.jinja2")

    config.add_resource_manager(mgr)
    #config.add_view(".DbView", name='view', context=Resource,
