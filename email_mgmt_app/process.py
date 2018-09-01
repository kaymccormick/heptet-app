import json
from typing import Dict

from sqlalchemy import Column

from email_mgmt_app.adapter import IAdapter
from pyramid_jinja2 import Environment

SettingsType = Dict[str, str]
TemplateEnvironmentType = Environment


class ProcessContext:
    def __init__(self, settings: SettingsType, template_env: TemplateEnvironmentType, adapter: IAdapter):
        self._settings = settings
        self._template_env = template_env

    @property
    def settings(self):
        return self._settings

    @settings.setter
    def settings(self, new):
        self._settings = new

    @property
    def template_env(self):
        return self._template_env

    @template_env.setter
    def template_env(self, new):
        self._template_env = new


class BaseProcessor:
    def __init__(self, pcontext):
        self._pcontex = pcontext

    @property
    def pcontext(self):
        return self._pcontex

    @pcontext.setter
    def pcontext(self, new):
        self._pcontex = new

class ViewProcessor(BaseProcessor):
    def __init__(self, obj):
        self._obj = obj

    def process(self):
        return
    pass


class ModelProcessor:
    pass


def setup_jsonencoder():
    def do_setup():
        old_default = json.JSONEncoder.default

        class MyEncoder(json.JSONEncoder):
            def default(self, obj):
                # logging.critical("type = %s", type(obj))
                v = None
                # This is not a mistake.
                if isinstance(obj, Column):
                    return ['Column', obj.name, obj.table.name]

                try:
                    v = old_default(self, obj)
                except:

                    assert False, type(obj)
                return v

        json.JSONEncoder.default = MyEncoder.default

    return do_setup
