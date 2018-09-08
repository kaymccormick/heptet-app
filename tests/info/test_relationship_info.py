import json
import logging
import sys

import pytest
from db_dump.schema import RelationshipSchema

logger = logging.getLogger(__name__)

#ripped from our model
_data = {'secondary': None, 'argument': 'email_mgmt_app.model.email_mgmt.Person', 'direction': 'MANYTOONE',
         'is_property': True, 'is_mapper': False, 'local_remote_pairs': [
        {'local': {'table': {'key': 'public_key'}, 'key': 'owner_id'},
         'remote': {'table': {'key': 'person'}, 'key': 'id'}}], 'mapper': {'local_table': {'key': 'person'}},
         'is_attribute': False, 'key': 'owner'}
_json = """
        {
          "secondary": null,
          "argument": "email_mgmt_app.model.email_mgmt.Person",
          "direction": "MANYTOONE",
          "is_property": true,
          "is_mapper": false,
          "local_remote_pairs": [
            {
              "local": {
                "table": {
                  "key": "public_key"
                },
                "key": "owner_id"
              },
              "remote": {
                "table": {
                  "key": "person"
                },
                "key": "id"
              }
            }
          ],
          "mapper": {
            "local_table": {
              "key": "person"
            }
          },
          "is_attribute": false,
          "key": "owner"
        }"""


@pytest.fixture
def my_json():
    return _json


@pytest.fixture
def my_data(my_json):
    d = json.loads(my_json)
    print(repr(d), file=sys.stderr)
    return d


@pytest.fixture
def my_relationship_info(relationship_schema, my_data):
    return relationship_schema.load(my_data)


@pytest.fixture
def relationship_schema():
    return RelationshipSchema()


def test_(my_relationship_info):
    logger.critical(my_relationship_info)
    assert 0
