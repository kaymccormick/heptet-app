import logging
import sys

logger = logging.getLogger(__name__)


def test_entity_view(entity_view_deriver, app_context, app_request, view_result):
    result = entity_view_deriver(app_context, app_request)
    logger.critical("result = %r", result)
    assert result
    print(result.text, file=sys.stderr)
    assert result is view_result

def test_entity_view_deriver_baseview(entity_view_deriver, app_context, app_request, ):
    result = entity_view_deriver(app_context, app_request)

