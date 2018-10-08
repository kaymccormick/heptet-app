import json

import pytest

from heptet_app.process import setup_jsonencoder


@pytest.mark.integration
def test_json_encoder(model_module):
    setup_jsonencoder()
    json.dumps({})
