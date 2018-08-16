from email_mgmt_app.entity import EntityCollectionView
from email_mgmt_app.entity.model.email_mgmt import Person
from pyramid.config import Configurator
from pyramid.request import Request


def includeme(config: Configurator):
    config.add_view(".PersonCollectionView",
                    route_name='person_collection',
                    renderer='templates/person/collection.jinja2')
    config.add_route('person_collection', '/persons')


class PersonCollectionView(EntityCollectionView[Person]):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)
        self._entity_type = Person

    def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)

