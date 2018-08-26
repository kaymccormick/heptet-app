from dataclasses import dataclass
from typing import AnyStr

from pyramid.config import Configurator


def register_entry_point(config, entry_point: AnyStr):
    appconfig = config.registry.email_mgmt_app
    appconfig.entry_points[entry_point.key] = entry_point


def includeme(config: Configurator):
    config.add_directive('register_entry_point', register_entry_point)

