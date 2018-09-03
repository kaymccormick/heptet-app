from pyramid_tm import explicit_manager


def get_request(request_factory, myapp_reg):
    request = request_factory({'wsgi.url_scheme': 'http', 'SERVER_NAME': 'localhost', 'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'})
    request.registry = myapp_reg
    request.tm = explicit_manager(request)
    # request.method = "GET"
    # request.url = "/"
    return request


def template_env():
    from jinja2 import Environment, PackageLoader, select_autoescape
    env = Environment(
        loader=PackageLoader('email_mgmt_app', 'templates'),
        autoescape=select_autoescape(default=False)
    )
    return env