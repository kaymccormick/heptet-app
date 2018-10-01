import logging
import sys

import lxml
import pytest
import transaction

logger = logging.getLogger(__name__)
from heptet_app.sqlalchemy_integration import get_tm_session, get_session_factory, get_engine


@pytest.fixture
def javascript_contenttypes():
    return ('application/javascript', 'text/plain')


@pytest.fixture
def packed_assets():
    return ('./node_modules/bootstrap/dist/css/bootstrap.min.css', './node_modules/bootstrap/dist/js/bootstrap.js',
            './node_modules/css-loader/index.js!./node_modules/bootstrap/dist/css/bootstrap.min.css',
            './node_modules/css-loader/lib/css-base.js', './node_modules/jquery/dist/jquery.js',
            './node_modules/popper.js/dist/esm/popper.js',
            './node_modules/raw-loader/index.js!./node_modules/jquery/dist/jquery.slim.min.js',
            './node_modules/script-loader/addScript.js',
            './node_modules/script-loader/index.js!./node_modules/jquery/dist/jquery.slim.min.js',
            './node_modules/style-loader/lib/addStyles.js', './node_modules/style-loader/lib/urls.js',
            './node_modules/webpack/buildin/global.js', './src/index.prod.js')


def init_database(engine, session):
    from heptet_app.model.meta import Base
    Base.metadata.create_all(engine)


@pytest.fixture
def sqlalchemy_engine(webapp_settings):
    return get_engine(webapp_settings)


@pytest.fixture
def session_factory(sqlalchemy_engine):
    return get_session_factory(sqlalchemy_engine)


@pytest.fixture
def transaction_manager():
    return transaction.manager


@pytest.fixture
def tm_session(session_factory, transaction_manager):
    return get_tm_session(session_factory, transaction_manager)


@pytest.fixture
def app_test_get(request, app_test):
    logger.critical("%s", request)


@pytest.fixture(params=['/', '/domain/form'])
def url(request):
    return request.param


@pytest.mark.integration
def test_webtest_urls(url, make_webtest):
    make_webtest(url)


@pytest.mark.integration
def test_webtest_domain_form(make_webtest):
    resp = make_webtest('/domain/form')
    logger.critical(resp.text)

    html = lxml.html.fromstring(resp.text)
    logger.critical("%s", resp.text)
    form_ = html.xpath("//form[@data-pyclass='Form']")
    assert form_ and 1 == len(form_)
    (form,) = form_
    assert form
    action = form.get('action')
    # assert action, "Form should have action attribute."
    method = form.get('method')
    # assert method, "Form shoud have method attribute."
    # assert method.upper() == 'POST'
    inputs = form.xpath("descendant::input")
    print([nput.get('name') for nput in inputs], sep="\n", file=sys.stderr)
    assert 2 == len(inputs)
