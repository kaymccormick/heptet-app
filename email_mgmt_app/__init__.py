import os

import ldap3
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.security import Allow, Authenticated
from pyramid_ldap3 import get_ldap_connector

import json

from email_mgmt_app.entity.model.meta import Base

# this is for ldap stuff
class RootFactory(object):
    __acl__ = [(Allow, Authenticated, 'view')]

    def __init__(self, request):
        pass

def groupfinder(dn, request):
    connector = get_ldap_connector(request)
    group_list = connector.user_groups(dn)
    if group_list is None:
        return None
    return [dn for dn, attrs in group_list]

def set_json_encoder(config, encoder):
    config.registry.json_encoder = encoder

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    f = open(settings['pidfile'], 'w')
    f.write("%d" % os.getpid())
    f.close()
    config = Configurator(settings=settings, root_factory=RootFactory)
    #config.add_request_method()
    config.include('pyramid_jinja2')
    config.include('.models')
#    config.include('.entity.model')
    config.include('.routes')
    config.include('.auth')
    config.include('.entity.domain.view') # ??


#    config.add_directive('json_encoder', set_json_encoder)
#    config.set_json_encoder(Encoder)
    config.set_authentication_policy(
        AuthTktAuthenticationPolicy('dmz3EpLAYqb\'y7s46QdeOOubiIUDV7U3',
                                    callback=groupfinder)
    )
    config.set_authorization_policy(
       ACLAuthorizationPolicy()
    )
    config.ldap_setup(
        'ldap://10.8.0.1'
    )

    config.ldap_set_login_query(
        base_dn='ou=People,DC=heptet,DC=us',
        filter_tmpl='(uid=%(login)s)',
        scope=ldap3.LEVEL,
    )

    config.ldap_set_groups_query(
        base_dn='ou=pyramid-groups,DC=heptet,DC=us',
        filter_tmpl='(&(objectCategory=groupOfNames)(member=%(userdn)s))',
        scope=ldap3.SUBTREE,
        cache_period=600,
    )

    # config.add_renderer('host', 'email_mgmt_app.renderer.HostRenderer')

    config.scan()
    return config.make_wsgi_app()
