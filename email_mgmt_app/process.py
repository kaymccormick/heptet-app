from typing import Dict

from pyramid_jinja2 import Environment

SettingsType = Dict[str, str]
TemplateEnvironmentType = Environment


class ProcessContext:
    def __init__(self, settings: SettingsType, template_env: TemplateEnvironmentType):
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
    pass


class ModelProcessor:
    pass


