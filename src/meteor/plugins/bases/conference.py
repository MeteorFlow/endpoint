"""
.. module: meteor.plugins.bases.conference
    :platform: Unix
    :copyright: (c) 2024 by MeteorFlow, see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kyle Tran <kyletran101.work@gmail.com>
"""
from meteor.plugins.base import Plugin


class ConferencePlugin(Plugin):
    type = "conference"

    def create(self, items, **kwargs):
        raise NotImplementedError
