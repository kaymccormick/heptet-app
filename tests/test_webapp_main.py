import pytest
from email_mgmt_app.webapp_main import wsgi_app

@pytest.mark.integration
def test_webapp_main(webapp_settings):
    import email_mgmt_app.webapp_main
    app = wsgi_app({}, **webapp_settings)
    assert app
