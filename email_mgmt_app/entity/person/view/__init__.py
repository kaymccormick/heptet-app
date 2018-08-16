from email_mgmt_app.entity import EntityCollectionView, EntityView
from email_mgmt_app.entity.model.email_mgmt import Person
from pyramid.config import Configurator
from pyramid.request import Request


def includeme(config: Configurator):
    config.add_view(".PersonCollectionView",
                    route_name='person_collection',
                    renderer='templates/person/collection.jinja2')
    config.add_route('person_collection', '/persons')
    config.add_view('.PersonView',
                    route_name='person',
                    renderer='templates/person/entity.jinja2')
    config.add_route('person', '/person/{id}')


class PersonCollectionView(EntityCollectionView[Person]):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)
        self._entity_type = Person


class PersonView(EntityView[Person]):
    def __init__(self, request: Request = None) -> None:
        super().__init__(request)
        self._entity_type = Person
