import ldap

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.response import Response

from pyramid.view import (
    view_config,
    forbidden_view_config,
    )

from pyramid.httpexceptions import HTTPFound

from pyramid.security import (
   Allow,
   Authenticated,
   remember,
   forget,
   )

from pyramid_ldap import (
    get_ldap_connector,
    groupfinder,
    )

@view_config(route_name='login',
             renderer='templates/login.pt')
@forbidden_view_config(renderer='templates/login.pt')
def login(request):
    url = request.current_route_url()
    login = ''
    password = ''
    error = ''

    if 'form.submitted' in request.POST:
        login = request.POST['login']
        password = request.POST['password']
        connector = get_ldap_connector(request)
        data = connector.authenticate(login, password)
        if data is not None:
            dn = data[0]
            headers = remember(request, dn)
            return HTTPFound('/', headers=headers)
        else:
            error = 'Invalid credentials'

    return dict(
        login_url=url,
        login=login,
        password=password,
        error=error,
        )

@view_config(route_name='root', permission='view')
def logged_in(request):
    return Response('OK')

@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return Response('Logged out', headers=headers)

class RootFactory(object):
    __acl__ = [(Allow, Authenticated, 'view')]
    def __init__(self, request):
        pass

def main(global_config, **settings):
    config = Configurator(root_factory=RootFactory)

    config.include('pyramid_ldap')

    config.set_authentication_policy(
        AuthTktAuthenticationPolicy('seekr1t',
                                    callback=groupfinder)
        )
    config.set_authorization_policy(
        ACLAuthorizationPolicy()
        )

    config.ldap_setup(
        'ldap://ldap.example.com',
        bind='CN=ldap user,CN=Users,DC=example,DC=com',
        passwd='ld@pu5er'
        )

    config.ldap_set_login_query(
        base_dn='CN=Users,DC=example,DC=com',
        filter_tmpl='(sAMAccountName=%(login)s)',
        scope = ldap.SCOPE_ONELEVEL,
        )

    config.ldap_set_groups_query(
        base_dn='CN=Users,DC=example,DC=com',
        filter_tmpl='(&(objectCategory=group)(member=%(userdn)s))',
        scope = ldap.SCOPE_SUBTREE,
        cache_period = 600,
        )

    config.add_route('root', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.scan('.')
    config.make_wsgi_app()