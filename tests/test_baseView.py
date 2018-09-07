from unittest import TestCase
from unittest.mock import MagicMock

from pyramid.testing import DummyRequest
from res import Resource, RootResource
from view import BaseView


def test_baseview():
    entity_type = MagicMock()
    name = 'my_resource'
    title = 'My Resource'
    context = Resource(name=name, parent=RootResource(), title=title,
                       entity_type=entity_type)
    request = DummyRequest()
    view = BaseView(context, request)
    assert view.request is request
    assert view.operation is None
    assert view.entry_point is None
    assert view.context is context
    r = view()
