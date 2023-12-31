"""
.. module: meteor.plugins.bases.contact
    :platform: Unix
    :copyright: (c) 2024 by MeteorFlow, see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kyle Tran <kyletran101.work@gmail.com>
"""
from meteor.plugins.base import Plugin


class ContactPlugin(Plugin):
    type = "contact"

    def get(self, key, **kwargs):
        raise NotImplementedError

    def create(self, key, **kwargs):
        raise NotImplementedError

    def update(self, key, **kwargs):
        raise NotImplementedError

    def delete(self, key, **kwargs):
        raise NotImplementedError
