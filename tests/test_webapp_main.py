import pytest
from email_mgmt_app.webapp_main import wsgi_app
from pyramid.interfaces import IRendererFactory


@pytest.mark.integration
def test_webapp_main(webapp_settings):
    import email_mgmt_app.webapp_main
    app = wsgi_app({}, **webapp_settings)
    registry = app.registry
    # check for default renderer factory
    factory = registry.queryUtility(IRendererFactory, '')

    assert factory
    assert 0
    assert app
