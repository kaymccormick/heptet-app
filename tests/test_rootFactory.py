import logging

from email_mgmt_app.root import RootFactory
from res import RootResource

logger = logging.getLogger(__name__)


def test_root_factory(app_request):
    rf = RootFactory(app_request)
    assert rf is not None
    r = rf()
    assert r is RootResource()
