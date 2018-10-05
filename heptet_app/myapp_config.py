import json
import logging
import sys

import pyramid_jinja2
from jinja2 import TemplateNotFound
from pyramid.config import Configurator
from pyramid.events import ContextFound, BeforeRender, NewRequest, ApplicationCreated
from pyramid.renderers import get_renderer
from pyramid.response import Response
from zope.component import IFactory, adapter
from zope.component.factory import Factory
from zope.interface import implementer

from heptet_app import Resource, RootResource, _get_root, EntryPointSchema
from heptet_app.impl import NamespaceStore
from heptet_app.interfaces import IResource, INamespaceStore, IEntryPointMapperAdapter, IObject, IEntryPoint
from heptet_app.util import _dump

logger = logging.getLogger(__name__)

TEMPLATE_ENV_NAME = 'template-env'


# jinja2_loader_template_path = settings['heptet_app.jinja2_loader_template_path'].split(':')
# env = Environment(loader=FileSystemLoader(jinja2_loader_template_path),
#                   autoescape=select_autoescape(default=False))
# config.registry.registerUtility(env, IJinja2Environment, 'app_env')
# config.add_request_method(lambda x: env, 'template_env')


def on_new_request(event):
    logger.debug("Resetting namespaces")
    registry = event.request.registry
    registry.registerUtility(NamespaceStore('form_name'), INamespaceStore, 'form_name')
    registry.registerUtility(NamespaceStore('namespace'), INamespaceStore, 'namespace')
    registry.registerUtility(NamespaceStore('global'), INamespaceStore, 'global')


def on_application_created(event):
    pass


def on_before_render(event):
    logger.critical("on_before_render: event=%s", event)
    val = event.rendering_val
    request = val['request'] = event['request']
    #    logger.critical("renderer = %s", request.renderer)
    # what happens if we clobber this? it also gets set for the form view
    entry_point = event['context'].entry_point
    if entry_point:
        val['entry_point_template'] = 'heptet_app:build/templates/entry_point/%s.jinja2' % entry_point.key
    logger.debug("VAL=%s", val)


def on_context_found(event):
    """
    Routine for overriding the renderer, called by pyramid event subscription. This does important things like provide the template
    environment via the context object (bad practice, though).
    :param event: the event
    :return:
    """
    request = event.request  # type: Request
    context = request.context  # type: Resource
    assert context is not None
    context.template_env = request.registry.queryUtility(pyramid_jinja2.IJinja2Environment, TEMPLATE_ENV_NAME)
    assert context.template_env
    if context.template_env is None:
        _dump(request.registry, cb=lambda fmt, *args: print(fmt % args, file=sys.stderr))

    import pprint
    pp = pprint.PrettyPrinter(width=120, stream=sys.stderr)
    pp.pprint(context)
    # print(textwrap.fill(repr(context), 1201), file=sys.stderr)
    # logger.critical("context is %r", context)

    if isinstance(context, Exception):
        return

    if hasattr(context, "entity_type"):
        # sets incorrect template
        def try_template(template_name):
            try:
                logger.debug("trying template %s", template_name)
                get_renderer(template_name).template_loader().render({})
                return True
            except TemplateNotFound as ex:
                return False
            except:
                return True

        entity_type = context.entity_type
        renderer = None

        # template selection
        if entity_type is not None:
            renderer = "templates/entity/%s.jinja2" % context.__name__

            if renderer:
                logger.debug("selecting %s for %s", renderer, request.path_info)
                request.override_renderer = renderer

        return True


def set_json_encoder(config, encoder):
    config.registry.json_encoder = encoder


@adapter(IObject)
@implementer(IEntryPointMapperAdapter)
class MapperProperty:
    def __init__(self, obj):
        self._obj = obj
        self._mapper = None

    @property
    def mapper(self):
        return self._mapper

    @mapper.setter
    def mapper(self, new):
        self._mapper = new


def entry_point_content(context, request):
    entry_point = request.registry.getUtility(IEntryPoint, request.subpath[0])
    vam = VirtualAssetManager()
    process_view(request.registry,
                 config=ProcessViewsConfig(),
                 proc_context=ProcessContext({}, context.template_env,

                                             vam),

                 entry_point=entry_point)

    logger.critical("v = %r", vam.assets[entry_point].content)
    # (v,) = vam.asset_content.values()

    return Response(vam.assets[entry_point].content)


def entry_points_json(context, request):
    utilities_for = request.registry.getUtilitiesFor(IEntryPoint)
    eps = list(map(lambda x: x[1], utilities_for))
    vam = VirtualAssetManager()
    for ep in eps:
        process_view(request.registry, config=ProcessViewsConfig(),
                     proc_context=ProcessContext({}, context.template_env, vam),
                     entry_point=ep);
        ep.content = vam.assets[ep].content
    s = EntryPointSchema()

    return Response(json.dumps({'entry_points': s.dump(eps, many=True)}))


def includeme(config: Configurator):
    config.include('.template')

    # we dont use this but its useful to remember how to do it
    # desc = 'request method template_env'
    # disc = ('add-request-method', 'template_env')
    # intr = config.introspectable('add-request-method', 'template_env', 'template_env request method',
    #                              'app request methods')

    config.add_request_method(
        lambda request: request.registry.getUtility(pyramid_jinja2.IJinja2Environment, TEMPLATE_ENV_NAME),
        'template_env')

    # what is the difference between posting an action versus registering the viwe in the cofnig??\\
    config.action(None, config.add_view, kw=dict(context=RootResource, renderer="heptet_app:templates/main_child.jinja2"))
    #    config.action(disc, _add_request_method, introspectables=(intr,), order=0)

    epj = _get_root().sub_resource('entry_points_json', None)
    config.add_view(entry_points_json, context=type(epj), renderer='json')
    _get_root().sub_resource('entry_points', None)
    config.add_view(entry_point_content, name='content', context=type(_get_root().sub_resource('entry_point', None)),
                    renderer='json')

    config.include('.entrypoint')
    factory = Factory(Resource, 'resource',
                      'ResourceFactory', (IResource,))
    config.registry.registerUtility(factory, IFactory, 'resource')

    config.registry.registerAdapter(MapperProperty, (IObject,), IEntryPointMapperAdapter)

    config.add_subscriber(on_context_found, ContextFound)
    config.add_subscriber(on_before_render, BeforeRender)
    config.add_subscriber(on_new_request, NewRequest)
    config.add_subscriber(on_application_created, ApplicationCreated)
