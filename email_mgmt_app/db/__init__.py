from pyramid.config import Configurator

from ..entity.view import BaseView
from ..res import ResourceRegistration, ResourceManager


class DbView(BaseView):
    def __call__(self, *args, **kwargs):
        return {}


def includeme(config: Configurator):
    mgr = ResourceManager(config, None)
    config.register_resource(ResourceRegistration('db', view=DbView), mgr)
    mgr.operation('view', DbView)
