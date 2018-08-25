import logging
import os

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.events import ContextFound
from pyramid.interfaces import IViewMapperFactory, IViewMapper
from pyramid.request import Request
from pyramid.viewderivers import DefaultViewMapper
from zope.interface import provider, implementer

from email_mgmt_app.predicate import EntityNamePredicate, EntityTypePredicate
from email_mgmt_app.res import NodeNamePredicate
from email_mgmt_app.res import Resource, RootResource, ResourceManager
from email_mgmt_app.root import RootFactory
from email_mgmt_app.security import groupfinder
from email_mgmt_app.template import TemplateManager
from email_mgmt_app.util import munge_dict
from jinja2 import Environment


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
    def _munge_view(request):
        resp = request.wrapped_response
        return munge_dict(request, resp)

    config.add_view(_munge_view, '_munge_view')

    config.include('pyramid_jinja2')
    config.include('.viewderiver')

    config.registry.email_mgmt_app_resources = RootResource({}, ResourceManager(config, name='', title='', node_name=''))
    config.include('.res')

    #config.add_directive('')

    config.include('.exceptions')

    config.include('.entity.model.email_mgmt')

    config.commit()

    config.include('.db')


    # config.include('.entityview.domain')
    # config.include('.entityview.host')
    # config.include('.entityview.email_address')
    # config.include('.entityview.recipient')
    # config.include('.entityview.organization')
    # config.include('.entityview.person')
    # config.include('.entityview.publickey')
    # config.include('.entityview.file_upload')
    # config.include('.entityview.file')

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
