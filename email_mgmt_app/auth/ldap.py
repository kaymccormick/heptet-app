import ldap3
from pyramid.security import remember

from pyramid.httpexceptions import HTTPFound

from pyramid_ldap3 import get_ldap_connector

from pyramid.view import forbidden_view_config, view_config
from email_mgmt_app.util import munge_dict


def includeme(config):
    config.include('pyramid_ldap3')
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


def ldap_groupfinder(dn, request):
    connector = get_ldap_connector(request)
    group_list = connector.user_groups(dn)
    if group_list is None:
        return None
    return [dn for dn, attrs in group_list]

##@view_config(route_name='login',
#             renderer='templates/login.jinja2')
#@forbidden_view_config(renderer='templates/login.jinja2')
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

    return munge_dict(request, dict(
        login_url=url,
        login=login,
        password=password,
        error=error,
        ))
