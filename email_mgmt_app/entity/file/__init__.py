from res.resource import ResourceRegistration, Resource, ResourceManager
from pyramid.config import Configurator

from email_mgmt_app.entity.model.email_mgmt import File
from email_mgmt_app.entity import EntityView, EntityAddView


def includeme(config: Configurator) -> None:
    res_mgr = ResourceManager(config, File)
    config.register_resource(
        ResourceRegistration('File', view=FileView, entity_type=File),
        res_mgr
    )

    res_mgr.operation('view', ".FileView")
    config.add_view(".FileView", name='view', context=Resource,
                    entity_type=File,
                    )

    res_mgr.operation('add', '.FileAddView')
    config.add_view('.FileAddView', name='add', context=Resource,
                    entity_type=File)

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
