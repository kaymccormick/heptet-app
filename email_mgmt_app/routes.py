def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('host_create', '/host/create')
    config.add_route('main', '/')
    config.add_route('host', '/host/{id}')
    config.add_route('root', '/root')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

