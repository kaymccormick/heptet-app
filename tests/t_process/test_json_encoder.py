import json

from email_mgmt_app.process import setup_jsonencoder


def test_json_encoder(model_module):
    setup_jsonencoder()
    json.dumps({})
