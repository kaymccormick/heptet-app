from __future__ import annotations

import logging

from email_mgmt_app import default_entry_point, IEntryPoint
from pyramid.config import Configurator

logger = logging.getLogger(__name__)

def register_entry_point(config, entry_point: IEntryPoint):
    config.registry.registerUtility(entry_point, IEntryPoint, entry_point.key)


def includeme(config: 'Configurator'):
    def do_action():
        pass
        # config.registry.registerAdapter(MyCollector, [ICollectorContext], ICollector)

    # FIXME rethink this directive?
    config.add_directive('register_entry_point', register_entry_point)
    register_entry_point(config, default_entry_point())
    config.action(None, do_action)
