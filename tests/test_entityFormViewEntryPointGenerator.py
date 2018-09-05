from unittest.mock import MagicMock

from pyramid_tm.tests import DummyRequest
from zope.component import adapter
from zope.interface import implementer

from email_mgmt_app.entity import EntityFormViewEntryPointGenerator, ITemplateVariable
from interfaces import ITemplateSource, ITemplate, ICollector
from pyramid_jinja2 import IJinja2Environment


def test_generate():
    request = DummyRequest()

    # components = request.registry
    # @adapter(ITemplateVariable)
    # @implementer(ICollector)
    # class MyMock(MagicMock):
    #     def __init__(self, var):
    #         super().__init__()
    #
    # #mock = MyMock()
    # components.registerAdapter(MagicMock, [ITemplateSource], ITemplate)
    # components.registerAdapter(MyMock, [ITemplateVariable], ICollector)
    #
    ep = MagicMock()

    # request.registry.registerUtility(MagicMock(), IJinja2Environment, 'app_env')
    epg = EntityFormViewEntryPointGenerator(ep, request)
    epg.generate()