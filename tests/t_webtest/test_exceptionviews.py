import pytest
import logging
from pyramid.exceptions import NotFound
from webob import Response
from webtest import AppError

logger = logging.getLogger(__name__)


@pytest.mark.integration
def test_exceptionviews_404(app_test):
    response = app_test.get('/random', expect_errors=True) # type: Response
    assert 404 == response.status_int
    logger.critical("%s", response.text)


