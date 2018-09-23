import logging
import sys
from typing import Generic, TypeVar, AnyStr

logger = logging.getLogger(__name__)
from unittest.mock import patch, MagicMock, call, PropertyMock

from lxml import html

from email_mgmt_app.form import FormOptionElement


class MyMagic(MagicMock):
    pass

T = TypeVar('T')


class Property(Generic[T]):
    def __init__(self, obj, name, init_value: T = None) -> None:
        super().__init__()
        self._obj = obj
        self._name = name
        self._value = init_value

    def __get__(self, instance, owner) -> T:
        assert self is instance
        return self._value

    def __set__(self, instance, value: T):
        assert self is instance
        self._value = value
        setattr(self._obj, self._name, value)

    def __call__(self, *args):
        if args:
            self._value = args[0]
            setattr(self._obj, self._name, args[0])
        else:
            return self._value


def test_formoptionelement_init():
    factory = html.Element
    map1 = dict()
    map2 = dict()

    def make_html(*args, **kwargs):
        elem = factory(*args, **kwargs)
        mock1 = MyMagic(wraps=elem, name="<%s>" % args[0])
        property_any_str_ = Property[AnyStr](elem, 'text')
        prop_mock = PropertyMock(wraps=property_any_str_, new_callable=MyMagic)
        type(mock1).text = prop_mock
        text_ = elem.__class__.text
        logger.critical("%r", dir(text_))
        # type(mock1).text = PropertyMock(wraps=text_, name="%s:text" % args[0])
        map1[id(mock1)] = elem
        map2[id(mock1)] = prop_mock
        return mock1

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
    val = list(map1.values()).pop(0)

    logger.critical("%r", val)






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
    assert 0, map1[key].text

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

    assert 0
