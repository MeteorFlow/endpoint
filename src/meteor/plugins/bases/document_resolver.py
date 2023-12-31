"""
.. module: meteor.plugins.bases.document
    :platform: Unix
    :copyright: (c) 2024 by MeteorFlow, see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kyle Tran <kyletran101.work@gmail.com>
"""
from meteor.plugins.base import Plugin


class DocumentResolverPlugin(Plugin):
    type = "document-resolver"

    def get(self, items, **kwargs):
        raise NotImplementedError
