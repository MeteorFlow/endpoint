"""
.. module: meteor.plugins.bases.signal_consumer
    :platform: Unix
    :copyright: (c) 2022 by MeteorFlow Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kyle Tran <kyletran101.work@gmail.com>
"""
from meteor.plugins.base import Plugin


class SignalConsumerPlugin(Plugin):
    type = "signal-consumer"

    def consume(self, **kwargs):
        raise NotImplementedError

    def delete(self, **kwargs):
        raise NotImplementedError
