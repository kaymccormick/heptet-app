import pytest
from heptet_app.webapp_main import wsgi_app
from pyramid.interfaces import IRendererFactory


@pytest.mark.integration
def test_webapp_main(webapp_settings):
    import heptet_app.webapp_main
    app = wsgi_app({}, **webapp_settings)
    registry = app.registry
    # check for default renderer factory
    factory = registry.queryUtility(IRendererFactory, '')

    assert factory
    assert app
