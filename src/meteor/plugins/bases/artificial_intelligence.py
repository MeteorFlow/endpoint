"""
.. module: meteor.plugins.bases.artificial_intelligence
    :platform: Unix
    :copyright: (c) 2024 by MeteorFlow, see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kyle Tran <kyletran101.work@gmail.com>
"""
from meteor.plugins.base import Plugin


class ArtificialIntelligencePlugin(Plugin):
    type = "artificial-intelligence"

    def chat(self, items, **kwargs):
        raise NotImplementedError

    def completion(self, items, **kwargs):
        raise NotImplementedError

    def summarization(self, items, **kwargs):
        raise NotImplementedError
