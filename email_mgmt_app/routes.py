def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('host_create', '/host/create')
    config.add_route('root', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

