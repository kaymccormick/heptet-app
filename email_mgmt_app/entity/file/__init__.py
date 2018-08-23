from sqlalchemy import Integer

from email_mgmt_app.res import ResourceRegistration, Resource, ResourceManager, OperationArgument
from pyramid.config import Configurator

from email_mgmt_app.entity.model.email_mgmt import File
from email_mgmt_app.entity import EntityView, EntityAddView


def includeme(config: Configurator) -> None:
    registration = ResourceManager.reg('File', default_view=FileView, entity_type=File)
    res_mgr = ResourceManager(config, registration)

    res_mgr.operation('view', ".FileView", [OperationArgument("id", Integer)])
    config.add_view(".FileView", name='view', context=Resource,
                    entity_type=File,
                    )

    res_mgr.operation('add', '.FileAddView', [])
    config.add_view('.FileAddView', name='add', context=Resource,
                    entity_type=File)
    config.add_resource_manager(res_mgr)

    # res_mgr.operation('form', ".FileFormView")
    # config.add_view('.FileFormView', name='form',
    #                 context=Resource, entity_type=File)
    #
    # res_mgr.operation('list', ".FileCollectionView")
    # config.add_view(
    #     ".FileCollectionView",
    #     name='list',
    #     context=Resource,
    #     entity_type=File,
    # )


class FileView(EntityView[File]):
    pass


class FileAddView(EntityAddView[File]):
    pass
