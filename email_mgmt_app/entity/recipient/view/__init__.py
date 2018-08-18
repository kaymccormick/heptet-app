from email_mgmt_app.entity import EntityCollectionView
from email_mgmt_app.entity.model.email_mgmt import Recipient
from pyramid.config import Configurator
from pyramid.request import Request


def includeme(config: Configurator):
    pass
#    config.add_view(".RecipientCollectionView", route_name="recipient_collection_view",
#                    renderer='templates/recipient/collection_view.jinja2', entity_type=Recipient)
#    config.add_route('recipient_collection_view', '/recipients')

class RecipientCollectionView(EntityCollectionView[Recipient]):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)
        self._entity_type = Recipient
