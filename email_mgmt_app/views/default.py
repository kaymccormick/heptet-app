from pyramid.httpexceptions import HTTPFound
from pyramid.request import Request
from pyramid.response import Response
from pyramid.security import remember, forget
from pyramid.view import forbidden_view_config

from sqlalchemy.orm import Query

from email_mgmt_app.entity.model.email_mgmt import ServiceEntry, Host
from email_mgmt_app.util import munge_dict
from email_mgmt_app.security import check_password, USERS


#@view_config(route_name='service', renderer='../templates/service/service.jinja2')
def service_view(request: Request) -> dict:
    service = request.dbsession.query(ServiceEntry).filter(ServiceEntry.id == request.matchdict['id']).first()
    hosts = request.dbsession.query(Host).all()
    return { 'service': service, 'hosts': hosts, 'route_path': request.route_path }

#@view_config(route_name='service_list', renderer='../templates/service/service_list.jinja2')
def service_list_view(request: Request) -> dict:
    entry__all = request.dbsession.query(ServiceEntry).order_by(ServiceEntry.port_num, ServiceEntry.protocol_name).all()
    hosts = request.dbsession.query(Host).all()
    return { 'services': entry__all , 'hosts': hosts, 'route_path': request.route_path }


#@view_config(route_name='main', permission='view', renderer='templates/main_child.jinja2')
def main_view(request: Request) -> dict:
    q = request.dbsession.query(Host) # type: Query
    need_paths_for = ['service_list']
    paths = { }
    for path in need_paths_for:
        paths[path] = request.route_path("service_list")

    if q.count() == 0:
        hosts = [ ]
    else:
        hosts = q.all()
    return munge_dict(request, {'hosts': hosts, 'paths': paths})


db_err_msg = "Pyramid is having a problem using your SQL database."

#@view_config(route_name='login',
#             renderer='templates/login.jinja2')
@forbidden_view_config(renderer='templates/login.jinja2')
def login(request):
    url = request.current_route_url()
    login = ''
    password = ''
    error = ''
    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/'  # never use login form itself as came_from
    came_from = request.params.get('came_from', referrer)

    if 'form.submitted' in request.POST:
        login = request.POST['login']
        password = request.POST['password']

        hashed_pw = USERS.get(login)
        if hashed_pw and check_password(password, hashed_pw):
            headers = remember(request, login)
            return HTTPFound(location=came_from,
                             headers=headers)
        message = 'Failed login'

    return munge_dict(request, dict(
        login_url=url,
        login=login,
        password=password,
        error=error,
        ))

#@view_config(route_name='root', permission='view')
def logged_in(request):
    return Response('OK')

#@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return Response('Logged out', headers=headers)

def host_form_defs(request):
    return { "action": request.route_path('host_create') }
