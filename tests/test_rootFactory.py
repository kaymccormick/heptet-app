import logging

from email_mgmt_app import get_root, RootResource

logger = logging.getLogger(__name__)


def test_root_factory(app_request):
    root = get_root(app_request)
    # this fails because root factory relies on a regostered RootResource
    logger.warning("typ is %s", type(root))
    logger.warning("r is %s", root)
    assert isinstance(root, RootResource)
