"""
.. module: meteor.plugins.bases.source
    :platform: Unix
    :copyright: (c) 2024 by MeteorFlow, see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kyle Tran <kyletran101.work@gmail.com>
"""
from meteor.plugins.base import Plugin


class SourcePlugin(Plugin):
    type = "source"

    def get(self, **kwargs):
        raise NotImplementedError
