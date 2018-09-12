from pyramid_tm import explicit_manager
from webob.request import environ_from_url


def get_request(request_factory, myapp=None, registry=None):
    environ = environ_from_url('/')
    # environ = {'wsgi.url_scheme': 'http',
    #            'wsgi.version'
    #            'REMOTE_ADDR': '127.0.0.1',
    #            'SERVER_NAME': 'localhost',
    #            'SCRIPT_NAME': '',
    #            'SERVER_PORT': 80,
    #            'SERVER_PROTOCOL': 'HTTP/1.1',
    #            'REQUEST_METHOD': 'GET',
    #            'PATH_INFO': ''}
    if myapp:
        context = myapp.request_context(environ)
        # context.begin()
        request = context.request
    else:
        request = request_factory(environ)
        request.registry = registry
        request.tm = explicit_manager(request)
    return request


def template_env():
    from jinja2 import Environment, PackageLoader, select_autoescape
    env = Environment(
        loader=PackageLoader('email_mgmt_app', 'templates'),
        autoescape=select_autoescape(default=False)
    )
    return env
