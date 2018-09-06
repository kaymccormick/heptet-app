from pyramid_tm import explicit_manager


def get_request(request_factory, myapp):
    environ = {'wsgi.url_scheme': 'http',
               'REMOTE_ADDR': '127.0.0.1',
               'SERVER_NAME': 'localhost',
               'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'}
    context = myapp.request_context(environ)
    #context.begin()
    request = context.request
#    request = request_factory()
#    request.registry = myapp.registry
#    request.tm = explicit_manager(request)
    return request


def template_env():
    from jinja2 import Environment, PackageLoader, select_autoescape
    env = Environment(
        loader=PackageLoader('email_mgmt_app', 'templates'),
        autoescape=select_autoescape(default=False)
    )
    return env
