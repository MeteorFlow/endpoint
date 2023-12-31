"""
.. module: meteor.plugins.bases.monitor
    :platform: Unix
    :copyright: (c) 2024 by MeteorFlow, see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
from meteor.plugins.base import Plugin


class MonitorPlugin(Plugin):
    type = "monitor"

    def get_status(self, **kwargs):
        raise NotImplementedError
