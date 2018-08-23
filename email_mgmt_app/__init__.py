import logging
import os

from pyramid.events import ContextFound
from pyramid.renderers import RendererHelper
from pyramid.request import Request

from jinja2 import Environment
from .template import TemplateManager
from .util import munge_dict
from .res import Resource, RootResource, ResourceManager
from .entity import EntityView
from .res import NodeNamePredicate
from .res import register_resource
from .predicate import EntityNamePredicate, EntityTypePredicate
from pyramid.viewderivers import INGRESS, VIEW

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from .root import RootFactory
from .security import groupfinder


def set_renderer(event):
    """
    Routine for overriding the renderer, called by pyramid event subscription
    :param event: the event
    :return:
    """
    request = event.request # type: Request
    context = request.context # type: Resource
    if context.entity_type:
        renderer = "templates/%s/%s.jinja2" % (context.entity_type.__name__.lower(),
                                               request.view_name.lower())
        logging.debug("selecting %s for %s", renderer, request.path_info)

        request.override_renderer = renderer
        return True


def set_json_encoder(config, encoder):
    config.registry.json_encoder = encoder


def munge_view(view, info):
    def wrapper_view(context, request):
        original_view = info.original_view
        response = view(context, request)

        if '__getattr__' in response.__dict__:
            response = munge_dict(request, response)

        return response
    return wrapper_view


def entity_view(view, info):

    et = info.options.get('entity_type')
    if et is not None:
        logging.info("original view = %s", repr(info.original_view))
        def wrapper_view(context, request):
            original_view = info.original_view

            renderer = None
            if isinstance(original_view, EntityView):
                # is this still in effect?
                assert False
                renderer = "    templates/%s/%s.jinja2" % (original_view.entity_type.__name__.lower(),
                                                       original_view.entity_type.__name__.lower())
            if renderer:
                request.override_renderer = renderer
            original_view._entity_type = et
            response = view(context, request)
            return response
            # tmpl = "templates/main_child.jinja2"
            # renderer = get_renderer(tmpl)
            # return renderer(response, { 'renderer_name': tmpl, 'view': view, 'context': context, 'request': request})
        return wrapper_view
    return view


def get_root(request: Request):
    return RootFactory(request)

# def load_global_templates(config):
#     tmpls = ['templates/left_sidebar.jinja2']
#
#     for template in tmpls:



def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    if 'pidfile' in settings.keys():
        f = open(settings['pidfile'], 'w')
        f.write("%d" % os.getpid())
        f.close()

    config = Configurator(settings=settings, root_factory=RootFactory)
    config.include('pyramid_jinja2')

    config.registry.email_mgmt_app_resources = RootResource({}, ResourceManager(config, ResourceManager.reg('', 'Root Resource', '')))
    config.include('.res')

    #config.add_directive('')

    config.include('.db')
    config.include('.entity.model.email_mgmt')
    config.include('.entity.domain.view')
    config.include('.entity.host.view')
    config.include('.entity.email_address.view')
    config.include('.entity.recipient.view')
    config.include('.entity.organization.view')
    config.include('.entity.person.view')
    config.include('.entity.publickey.view')
    config.include('.entity.file_upload.view')
    config.include('.entity.file')

    config.include('.routes')
    config.include('.auth')
    config.include('.views')

    config.set_authentication_policy(
        AuthTktAuthenticationPolicy(settings['email_mgmt_app.secret'],
                                    callback=groupfinder)
    )
    config.set_authorization_policy(
       ACLAuthorizationPolicy()
    )

    renderer_pkg = 'pyramid_jinja2.renderer_factory'
    logging.debug("adding renderer %s", renderer_pkg)
    config.add_renderer(None, renderer_pkg)

    logging.debug("registering event subscriber")
    config.add_subscriber(set_renderer, ContextFound)

    logging.debug("registering view deriver")
    entity_view.options = ('entity_type',)
    config.add_view_deriver(entity_view, under=INGRESS)
    config.add_view_deriver(munge_view)

    logging.debug("registering view predicates")
    config.add_view_predicate('entity_name', EntityNamePredicate)
    config.add_view_predicate('entity_type', EntityTypePredicate)
    config.add_view_predicate('node_name', NodeNamePredicate)

    logging.debug("Comitting configuration")
    config.commit()

    env = config.get_jinja2_environment() # type: Environment
#    env.globals[]
    tmpl_mgr = TemplateManager(config)

    # experimental template preload
    renderers = { }
    for x in os.walk("templates"):
        for y in x[2]:
            path = os.path.join(x[0], y)
            tmpl_mgr.add_template(path)

    config.registry['app_renderers'] = renderers

    config.registry['email_mgmt_app_resources'] = None
    # Configure our Root Factory for when it is instantiated on a per-request basis
    RootFactory.populate_resources(config)

    #config.scan()
    return config.make_wsgi_app()
