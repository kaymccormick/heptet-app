import logging
import sys

import pytest

logger = logging.getLogger(__name__)


@pytest.fixture
def entry_point_1(make_entry_point, resource_manager_mock):
    logger.debug("Returning fixture entry_point_1")
    return make_entry_point(
        resource_manager_mock,
        'test1',
    )


def test_entrypoint_init_generator(
        entry_point_1,
        root_namespace_store,
        jinja2_env_mock,
        make_entity_form_view_entry_point_generator,
        app_registry_mock,
):
    generator = entry_point_1.init_generator(
        app_registry_mock,
        root_namespace_store,
        jinja2_env_mock,
        make_entity_form_view_entry_point_generator,
    )
    assert generator
    # TODO


def test_entrypoint_generate(
        entry_point_1,
        root_namespace_store,
        jinja2_env_mock,
        make_entity_form_view_entry_point_generator,
        app_registry_mock,
):
    generator = entry_point_1.init_generator(
        app_registry_mock,
        root_namespace_store,
        jinja2_env_mock,
        make_entity_form_view_entry_point_generator,
    )
    assert generator
    x = generator.generate()
    print(x, file=sys.stderr)
    # TODO
