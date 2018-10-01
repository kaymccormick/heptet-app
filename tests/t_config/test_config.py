import copy
import json
import sys

#import pinject
import pytest

from heptet_app import get_root, ResourceSchema
from heptet_app.model import email_mgmt


# make_wsgi_app is a fixture, not our application!!
# not sure what we are testing here
@pytest.mark.integration
def test_my_config_model_package(
        make_wsgi_app, # this is a custom config!
        webapp_settings
):
    settings = copy.copy(webapp_settings)
    settings['model_package'] = email_mgmt
    app = make_wsgi_app({}, **settings)


@pytest.mark.integration
def test_my_config_2(make_wsgi_app, webapp_settings):
    #    obj_graph = pinject.new_object_graph(#only_use_explicit_bindings=True,
    #                                         modules=None)
    #    schema = obj_graph.provide(ResourceSchema)
    #
    assert 0
    settings = copy.copy(webapp_settings)
    settings['model_package'] = email_mgmt
    app = make_wsgi_app({}, **settings)
    root = get_root(None)
    s = ResourceSchema()
    json.dump(s.dump(root), fp=sys.stderr)

