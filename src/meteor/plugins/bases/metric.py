"""
.. module: meteor.plugins.bases.metric
    :platform: Unix
    :copyright: (c) 2024 by MeteorFlow, see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kyle Tran <kyletran101.work@gmail.com>
"""
from meteor.plugins.base import Plugin


class MetricPlugin(Plugin):
    type = "metric"

    def gauge(self, name, value, tags=None):
        raise NotImplementedError

    def counter(self, name, value=None, tags=None):
        raise NotImplementedError

    def timer(self, name, value, tags=None):
        raise NotImplementedError
