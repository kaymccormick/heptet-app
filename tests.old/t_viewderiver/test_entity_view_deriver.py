import json
import logging
from collections import Set
from unittest.mock import call

import pytest
import sys

from heptet_app import viewderiver
from heptet_app import BaseView, ResourceSchema

logger = logging.getLogger(__name__)


#
#
# what is this testing, exactly??
#
# entity_view_deriver relies on the "resource_operation" fixture which is very generic

@pytest.mark.integration
def test_entity_view(entity_view_deriver, app_context, app_request, view_result):
    result = entity_view_deriver(app_context, app_request)
    logger.critical("result = %r", result)
    assert result
    print(result.text, file=sys.stderr)
    assert result is view_result


@pytest.mark.integration
def test_entity_view_deriver_baseview(
        make_entity_view_deriver,
        app_context,
        app_request,
        make_view_deriver_info,
        app_registry_mock,
        resource_operation_mock):
    baseview = BaseView(app_context, app_request)
    options = {'operation': resource_operation_mock}
    info = make_view_deriver_info(baseview, app_registry_mock, __name__, [], False, options)
    deriver = make_entity_view_deriver(baseview, info)
    result = deriver(app_context, app_request)
    schema = ResourceSchema()
    context = result['context']

    dump = schema.dump(context)
    logger.critical("%s", json.dumps(dump, indent=4, sort_keys=True))

def test_viewderiver_include(config_mock):
    viewderiver.includeme(config_mock)
    config_mock.assert_has_calls([call.add_view_deriver(viewderiver.entity_view, under='INGRESS')])
    assert set(('operation', 'mapper_info', 'node_name', 'entry_point')) == set(viewderiver.entity_view.options)
