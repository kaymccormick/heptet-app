import logging

from email_mgmt_app.root import RootFactory
from email_mgmt_app.res import RootResource

logger = logging.getLogger(__name__)


def test_root_factory(app_request):
    # this fails because root factory relies on a regostered RootResource
    rf = RootFactory()
    assert rf is not None
    r = rf(app_request)
    assert r is RootResource()
