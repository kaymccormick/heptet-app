def test_webapp_main(webapp_settings):
    import webapp_main
    app = webapp_main.wsgi_app({}, **webapp_settings)
    assert app
