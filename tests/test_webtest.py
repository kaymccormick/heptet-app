import logging
import re
import sys

import lxml.html
import pytest
from lxml import html
from webtest import TestApp
import transaction
import lxml

logger = logging.getLogger(__name__)
import email_mgmt_app.webapp_main
from sqlalchemy_integration import get_tm_session, get_session_factory, get_engine


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
    from model.meta import Base
    Base.metadata.create_all(engine)


@pytest.fixture
def webapp_factory():
    return email_mgmt_app.webapp_main.wsgi_app


@pytest.fixture
def webapp(webapp_factory, webapp_settings):
    return webapp_factory(None, **webapp_settings)


@pytest.fixture
def app_test(webapp):
    return TestApp(webapp)


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


@pytest.fixture
def make_webtest(sqlalchemy_engine, tm_session, app_test, javascript_contenttypes, packed_assets):
    def _webtest(url, debug=True):
        logger.warning("%s", sys.path)
        init_database(sqlalchemy_engine, tm_session)

        resp = app_test.get(url, expect_errors=True)
        if resp.status_int == 520:
            print(resp.text, file=sys.stderr)

        assert 200 == resp.status_int
        assert 'text/html' == resp.content_type
        assert 0 < resp.content_length
        root = lxml.html.document_fromstring(resp.text)
        assert root.tag == "html"

        if debug:
            print(html.tostring(root, encoding="unicode"), file=sys.stderr)

        _head = root.xpath("head")
        assert _head, "No head element"
        assert len(_head) == 1, "Too many head elements"
        (head,) = _head
        _title = head.xpath("title")
        assert _title, "No title Element"
        assert len(_title) == 1, "Too many title elements"

        logging.debug("type(root) = %s", type(root))
        scripts = root.xpath("//script")
        srcs = []
        for script in scripts:
            if 'src' in script.attrib:
                script_src = script.get('src')
                srcs.append(script_src)

        for src in srcs:
            print(src)
            srcresp = app_test.request(src)
            assert srcresp.content_type in javascript_contenttypes, ("%s" % srcresp.content_type)
            text = srcresp.text
            all = re.findall(r'^/\*\*\*/ "(.*)":$', text, re.MULTILINE)
            # print(*all, sep='\n')

        logging.debug("response text = %s", repr(resp.text))
        debug_dict = {}
        matches = re.findall(r'<!-- ([^ \t]*) = ([^ ]*) -->', resp.text)
        for (k, v) in matches:
            debug_dict[k] = v
            logging.debug("debug_dict[%s] = %s", k, v)

        for link in root.iterlinks():
            print(link[2])

        return (resp, root)

    return _webtest


@pytest.mark.integration
def test_webtest_urls(url, make_webtest):
    make_webtest(url)


@pytest.mark.integration
def test_webtest_domain_form(make_webtest):
    (resp, html) = make_webtest('/domain/form')
    logger.critical("%s", resp.text)
    form_ = html.xpath("//form[@data-pyclass='Form']")
    assert form_ and 1 == len(form_)
    (form,) = form_
    assert form
    action = form.get('action')
    #assert action, "Form should have action attribute."
    method = form.get('method')
    #assert method, "Form shoud have method attribute."
    #assert method.upper() == 'POST'
    inputs = form.xpath("descendant::input")
    print([nput.get('name') for nput in inputs], sep="\n", file=sys.stderr)
    assert 2 == len(inputs)

