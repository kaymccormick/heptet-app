import logging
from typing import AnyStr

from pyramid.config import Configurator
from pyramid.renderers import RendererHelper


class TemplateManager:
    def __init__(self, config: Configurator) -> None:
        self._config = config
        self._rs = {}

    def add_template(self, path: AnyStr):
        logging.debug("path = %s", path)
        self._rs[path] = RendererHelper(name=path,
                                        package='email_mgmt_app',
                                        registry=self._config.registry)
        logging.debug("renderer = %s", self._rs[path])

