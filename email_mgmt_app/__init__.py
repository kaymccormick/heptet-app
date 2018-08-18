import logging
import os

from .resource import NodeNamePredicate
from .root import register_resource
from email_mgmt_app.entity import EntityNamePredicate
from pyramid.viewderivers import INGRESS

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from .root import RootFactory
from .security import groupfinder

def set_json_encoder(config, encoder):
    config.registry.json_encoder = encoder

def entity_view(view, info):
    et = info.options.get('entity_type')
    if et is not None:
        logging.info("original view = %s", repr(info.original_view))
        def wrapper_view(context, request):
            info.original_view._entity_type = et
            response = view(context, request)
            return response
        return wrapper_view
    return view


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    if 'pidfile' in settings.keys():
        f = open(settings['pidfile'], 'w')
        f.write("%d" % os.getpid())
        f.close()

    config = Configurator(settings=settings, root_factory=RootFactory)

    config.add_directive('register_resource', register_resource)

    config.include('pyramid_jinja2')
    config.include('.entity.model.email_mgmt')
    config.include('.entity.domain.view')
    config.include('.entity.recipient.view')
    config.include('.entity.organization.view')
    config.include('.entity.person.view')
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

    # config.add_renderer('host', 'email_mgmt_app.renderer.HostRenderer')
    entity_view.options = ('entity_type',)
    config.add_view_deriver(entity_view, under=INGRESS)

    config.add_view_predicate('entity_name', EntityNamePredicate)
    config.add_view_predicate('node_name', NodeNamePredicate)
    config.commit()

    RootFactory.populate_resources(config)

    #config.scan()
    return config.make_wsgi_app()
