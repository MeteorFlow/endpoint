"""
.. module: meteor.plugins.bases.conversation
    :platform: Unix
    :copyright: (c) 2024 by MeteorFlow, see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kyle Tran <kyletran101.work@gmail.com>
"""
from meteor.plugins.base import Plugin


class ConversationPlugin(Plugin):
    type = "conversation"

    def create(self, items, **kwargs):
        raise NotImplementedError

    def add(self, items, **kwargs):
        raise NotImplementedError

    def send(self, items, **kwargs):
        raise NotImplementedError
