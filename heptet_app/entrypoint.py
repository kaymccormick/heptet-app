from pyramid.config import Configurator
from pyramid.request import Request

from heptet_app import IEntryPoint


def register_entry_point(config, entry_point: IEntryPoint):
    config.registry.registerUtility(entry_point, IEntryPoint, entry_point.key)


def includeme(config: 'Configurator'):
    # def do_action():
    #     pass

    config.add_directive('register_entry_point', register_entry_point)
    intr = config.introspectable('configuration include', 'entrypoint', 'entrypoint', 'include package')

    def _get_entry_points(request: Request):
        return request.registry.getUtilitiesFor(IEntryPoint)

    config.add_request_method(property(_get_entry_points), 'entry_points')
#    config.action(None, do_action, introspectables=intr)

