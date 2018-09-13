import copy
import json
import sys

import pytest

from email_mgmt_app import get_root, ResourceSchema
from model import email_mgmt


# we need to keep this somewhat synchronized!


# make_wsgi_app is a fixture, not our application!!

@pytest.mark.integration
def test_my_config(make_wsgi_app, webapp_settings):
    settings = copy.copy(webapp_settings)
    settings['model_package'] = email_mgmt
    app = make_wsgi_app({}, **settings)

@pytest.mark.integration
def test_my_config(make_wsgi_app, webapp_settings):
    settings = copy.copy(webapp_settings)
    settings['model_package'] = email_mgmt
    app = make_wsgi_app({}, **settings)
    root = get_root(None)
    s = ResourceSchema()
    json.dump(s.dump(root), fp=sys.stderr)
    assert 0
