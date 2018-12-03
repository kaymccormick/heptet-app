import json

from pyramid.response import Response

from heptet_app.mschema import EntryPointSchema
from heptet_app.interfaces import IResourceRoot, IEntryPointFactory
from heptet_app.process import VirtualAssetManager, process_view, ProcessContext
import marshmallow


def entry_points_json(context, request):
    assert marshmallow.__version__.startswith('3.')
    utilities_for = request.entry_points
    eps = list(map(lambda x: x[1], utilities_for))
    vam = VirtualAssetManager()
    for ep in eps:
        process_view(request.registry, config={},
                     proc_context=ProcessContext({}, context.template_env, vam),
                     entry_point=ep);
        ep.content = vam.assets[ep].content
    s = EntryPointSchema()

    return Response(json.dumps({'entry_points': s.dump(eps, many=True)}))


def includeme(config):
    resource_root = config.registry.getUtility(IResourceRoot)
    entry_point_factory = config.registry.getUtility(IEntryPointFactory)
    entry_points = resource_root.create_resource('entry_points', None)
    json_resource = entry_points.create_resource('json', None)

    def _action():
        config.add_view(entry_points_json, context=type(json_resource), renderer='json')

    config.action(None, _action)
