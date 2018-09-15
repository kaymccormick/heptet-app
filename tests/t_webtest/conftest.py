import sys

import pytest
from webtest import TestApp

import email_mgmt_app.webapp_main
from tests.conftest import logger


@pytest.fixture  # sqlalchemy_engine, tm_session,
def make_webtest(app_test):
    def _webtest(url, debug=True):
        logger.warning("%s", sys.path)
        # init_database(sqlalchemy_engine, tm_session)

        resp = app_test.get(url, expect_errors=True)
        return resp
        # if resp.status_int == 520:
        #     print(resp.text, file=sys.stderr)
        #
        # assert 200 == resp.status_int
        # assert 'text/html' == resp.content_type
        # assert 0 < resp.content_length
        # root = lxml.html.document_fromstring(resp.text)
        # assert root.tag == "html"
        #
        # if debug:
        #     print(html.tostring(root, encoding="unicode"), file=sys.stderr)
        #
        # _head = root.xpath("head")
        # assert _head, "No head element"
        # assert len(_head) == 1, "Too many head elements"
        # (head,) = _head
        # _title = head.xpath("title")
        # assert _title, "No title Element"
        # assert len(_title) == 1, "Too many title elements"
        #
        # logging.debug("type(root) = %s", type(root))
        # scripts = root.xpath("//script")
        # srcs = []
        # for script in scripts:
        #     if 'src' in script.attrib:
        #         script_src = script.get('src')
        #         srcs.append(script_src)
        #
        # for src in srcs:
        #     print(src)
        #     srcresp = app_test.request(src)
        #     assert srcresp.content_type in javascript_contenttypes, ("%s" % srcresp.content_type)
        #     text = srcresp.text
        #     all = re.findall(r'^/\*\*\*/ "(.*)":$', text, re.MULTILINE)
        #     # print(*all, sep='\n')
        #
        # logging.debug("response text = %s", repr(resp.text))
        # debug_dict = {}
        # matches = re.findall(r'<!-- ([^ \t]*) = ([^ ]*) -->', resp.text)
        # for (k, v) in matches:
        #     debug_dict[k] = v
        #     logging.debug("debug_dict[%s] = %s", k, v)
        #
        # for link in root.iterlinks():
        #     print(link[2])
        #
        # return (resp, root)

    return _webtest


@pytest.fixture
def app_test(webapp):
    return TestApp(webapp)


@pytest.fixture
def webapp(webapp_factory, webapp_settings):
    return webapp_factory(None, **webapp_settings)


@pytest.fixture
def webapp_factory():
    return email_mgmt_app.webapp_main.wsgi_app
