from jinja2.exceptions import TemplateNotFound
from pyramid.response import Response
import logging
from webtest import TestApp
logger = logging.getLogger(__name__)

def test_webtest_1(config_fixture, caplog):
    caplog.set_level(logging.WARNING)
    root = config_fixture.get_root_resource()
    config_fixture.add_view(lambda r: Response(""), context=type(root))
    app = config_fixture.make_wsgi_app()
    test_app = TestApp(app)
    try:
        resp = test_app.get('/', expect_errors=True)
    except TemplateNotFound as ex:
        logger.warning("Template %r not found", ex.name)
        raise ex
        
    logger.debug("resp is %r", resp)
    assert 0
    
