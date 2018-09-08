import logging

logger = logging.getLogger(__name__)


def test_entity_view(entity_view_deriver, app_context, app_request, view_result):
    result = entity_view_deriver(app_context, app_request)
    assert result
    assert result is view_result
