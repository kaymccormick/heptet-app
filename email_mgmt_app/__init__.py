import logging
import os

from email_mgmt_app.context import EntityResource
from email_mgmt_app.entity import EntityNamePredicate
from pyramid.viewderivers import INGRESS

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.security import Allow, Authenticated
from .security import groupfinder


class Resource(dict):
    pass


class RootFactory(Resource):
    root_resources = {}
    __acl__ = [(Allow, Authenticated, None),
               (Allow, Authenticated, 'view')]

    def __init__(self, request):
        super().__init__(RootFactory.root_resources)


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

def register_resource(config, name, resource):
    def register():
        if 'resources' not in config.registry.keys():
            config.registry['resources'] = {}

        config.registry['resources'][name] = resource

    config.action(None, register)


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
    config.commit()
    if config.registry['resources'] is not None:
        for (k, v) in config.registry['resources'].items():
            RootFactory.root_resources[k] = EntityResource(k, v)

    config.scan()
    return config.make_wsgi_app()
