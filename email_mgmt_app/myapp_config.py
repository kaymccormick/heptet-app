import logging
import sys

from jinja2 import TemplateNotFound
from pyramid.config import Configurator, PHASE2_CONFIG
from pyramid.events import ContextFound, BeforeRender, NewRequest, ApplicationCreated
from pyramid.interfaces import IRendererFactory, PHASE3_CONFIG
from pyramid.renderers import get_renderer
from pyramid_jinja2 import IJinja2Environment
from zope.component import IFactory
from zope.component.factory import Factory

import email_mgmt_app
from impl import NamespaceStore
from interfaces import IResource, INamespaceStore
from email_mgmt_app import RootResource, Resource
from webapp_main import logger

logger = logging.getLogger(__name__)


# jinja2_loader_template_path = settings['email_mgmt_app.jinja2_loader_template_path'].split(':')
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
    logger.debug("on_before_render: event=%s", event)
    val = event.rendering_val
    val['request'] = event['request']
    logger.debug("VAL=%s", val)


def on_context_found(event):
    """
    Routine for overriding the renderer, called by pyramid event subscription
    :param event: the event
    :return:
    """
    request = event.request  # type: Request
    context = request.context  # type: Resource
    context.template_env = request.registry.getAdapter(IJinja2Environment, 'template-env')
    import pprint
    pp = pprint.PrettyPrinter(width=120, stream=sys.stderr)
    pp.pprint(context)
    #print(textwrap.fill(repr(context), 1201), file=sys.stderr)
    #logger.critical("context is %r", context)

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

        if entity_type is not None:
            renderer = "templates/entity/%s.jinja2" % context.__name__

            if renderer:
                logger.debug("selecting %s for %s", renderer, request.path_info)
                request.override_renderer = renderer

        #     logger.debug("Type of entity_type is %s", type(entity_type))
        #     renderer = "templates/%s/%s.jinja2" % (entity_type.__name__.lower(),
        #                                            request.view_name.lower())
        #
        #     if not try_template(renderer):
        #         renderer = None
        #         if request.view_name:
        #             renderer = "templates/entity/%s.jinja2" % request.view_name.lower()
        # else:
        return True


def set_json_encoder(config, encoder):
    config.registry.json_encoder = encoder

def includeme(config: Configurator):
    config.include('..template')
    # FIXME should not need this

    desc = 'request method template_env'
    disc = ('add-request-method', 'template_env')
    intr = config.introspectable('add-request-method', 'template_env', 'template_env request method', 'app request methods')

    config.add_request_method(lambda request: request.registry.getUtility(IJinja2Environment, 'template-env'), 'template_env')

#    config.action(disc, _add_request_method, introspectables=(intr,), order=0)

    config.include('..entrypoint')
    factory = Factory(Resource, 'resource',
                      'ResourceFactory', (IResource,))
    config.registry.registerUtility(factory, IFactory, 'resource')

    config.add_subscriber(on_context_found, ContextFound)
    config.add_subscriber(on_before_render, BeforeRender)
    config.add_subscriber(on_new_request, NewRequest)
    config.add_subscriber(on_application_created, ApplicationCreated)

