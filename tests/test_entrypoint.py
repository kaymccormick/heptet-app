import logging

from entity import EntityFormViewEntryPointGenerator

logger = logging.getLogger(__name__)


def test_entrypoint_1(make_entry_point, resource_manager_mock, app_request, app_registry_mock, root_namespace_store,
                      jinja2_env_mock, make_entity_form_view_entry_point_generator):
    entry_point = make_entry_point(resource_manager_mock, 'test1', app_request, app_registry_mock, None, None)
    logger.critical("%r", entry_point)
    logger.critical("%r", entry_point.discriminator)
    entry_point.init_generator(app_registry_mock, root_namespace_store, jinja2_env_mock,
                               make_entity_form_view_entry_point_generator)
    assert entry_point.generator
    # TODO