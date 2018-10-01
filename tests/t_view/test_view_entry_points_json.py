import json
import logging

from heptet_app.myapp_config import entry_points_json

logger = logging.getLogger(__name__)


def test_view_entry_point_json_main(app_context_mock, app_request):
    c = app_context_mock
    logger.critical("app_context = %r", c)
    r = entry_points_json(c, app_request)
    data = json.loads(r.text)

    assert 0, repr(c.mock_calls) + "\n\n";
