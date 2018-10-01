def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('dist', '../build/dist')
    config.add_static_view('build', 'build')
    config.add_static_view('app1/dist', '../build/dist')
