import logging
import re
import sys
import textwrap

import pytest
import termcolor

logger = logging.getLogger(__name__)


@pytest.fixture
def entry_point_1(make_entry_point, resource_manager_mock, app_request, app_registry_mock):
    logger.debug("Returning fixture entry_point_1")
    return make_entry_point(
        resource_manager_mock,
        'test1',
        app_request,
        app_registry_mock,
        None,
        None,
    )


def test_entrypoint_init_generator(
        entry_point_1,
        root_namespace_store,
        jinja2_env_mock,
        make_entity_form_view_entry_point_generator,
        app_registry_mock,
):
    entry_point_1.init_generator(
        app_registry_mock,
        root_namespace_store,
        jinja2_env_mock,
        make_entity_form_view_entry_point_generator,
    )
    assert entry_point_1.generator
    # TODO

def test_entrypoint_generate(
        entry_point_1,
        root_namespace_store,
        jinja2_env_mock,
        make_entity_form_view_entry_point_generator,
        app_registry_mock,
):
    entry_point_1.init_generator(
        app_registry_mock,
        root_namespace_store,
        jinja2_env_mock,
        make_entity_form_view_entry_point_generator,
    )
    assert entry_point_1.generator
    x = entry_point_1.generator.generate()
    print(x, file=sys.stderr)
    # TODO
