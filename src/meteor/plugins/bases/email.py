"""
.. module: meteor.plugins.bases.email
    :platform: Unix
    :copyright: (c) 2024 by MeteorFlow, see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kyle Tran <kyletran101.work@gmail.com>
"""
from meteor.plugins.base import Plugin


class EmailPlugin(Plugin):
    type = "email"

    def send(self, items, **kwargs):
        raise NotImplementedError
