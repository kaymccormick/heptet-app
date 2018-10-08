import logging
import sys
from typing import AnyStr

import pytest

from tests import Property

logger = logging.getLogger(__name__)
from unittest.mock import patch, MagicMock, call, PropertyMock

from lxml import html

from heptet_app.form import FormOptionElement


class MyMagic(MagicMock):
    pass


@pytest.fixture
def wraps_html_mock(wrap_make_html):
    return MagicMock(wraps=wrap_make_html)


@pytest.fixture
def patch_element(wraps_html_mock):
    try:
        yield patch("lxml.html.Element", wraps_html_mock)
    finally:
        pass


def test_formoptionelement_init(
        monkeypatch_html,
):
    with pytest.raises(AssertionError):
        option = FormOptionElement('test', 1)
        value = '1'
        mock = option.element
        myhtml = option.as_html()
        logger.critical(myhtml)
        element = html.fromstring(myhtml)

        assert 'option' == element.tag.lower()
        assert value == element.get('value')
        assert 'test' == element.text
        assert 0


def test_formoptionelement_init_2():
    factory = html.Element
    map1 = dict()
    map2 = dict()

    def make_html(*args, **kwargs):
        elem = factory(*args, **kwargs)
        mock1 = MyMagic(wraps=elem, name="<%s>" % args[0])
        property_any_str_ = Property[AnyStr](elem, 'text')
        prop_mock = PropertyMock(wraps=property_any_str_, new_callable=MyMagic)
        type(mock1).text = prop_mock
        # mock1.text = MagicMock()
        text_ = elem.__class__.text
        logger.critical("%r", dir(text_))
        # type(mock1).text = PropertyMock(wraps=text_, name="%s:text" % args[0])
        map1[id(mock1)] = elem
        map2[id(mock1)] = prop_mock
        return mock1

    elem = make_html('foo')
    elem.text = 'bar'

    logger.critical(repr(elem.text))
    (key,) = map1.keys()

    mock = MagicMock(wraps=make_html)
    with patch("lxml.html.Element", mock):
        option = FormOptionElement('test', 1)

    value = '1'
    mock.assert_has_calls([call('option', {'value': value})])

    tostring = html.tostring

    def _tostring(element, **kwargs):
        return tostring(map1[id(element)], **kwargs)

    m = MyMagic(wraps=_tostring, name="html.tostring")
    myhtml = None
    with patch("lxml.html.tostring", m):
        myhtml = option.as_html()

    logger.critical("beep = %s", repr(option.element.text))

    logger.critical(myhtml)
    print("mock.mock_calls =", repr(mock.mock_calls), file=sys.stderr)

    element = html.fromstring(myhtml)

    assert 'option' == element.tag.lower()
    assert value == element.get('value')
    assert element.text == 'test'

    print(repr(m.mock_calls), file=sys.stderr)
    for key, val in map1.items():
        logger.critical("%r", val)
