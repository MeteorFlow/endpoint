"""
.. module: meteor.plugins.bases.mfa
    :platform: Unix
    :copyright: (c) 2023 by MeteorFlow Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kyle Tran <kyletran101.work@gmail.com>
"""
from meteor.plugins.base import Plugin


class MultiFactorAuthenticationPlugin(Plugin):
    type = "auth-mfa"

    def send_push_notification(self, items, **kwargs):
        raise NotImplementedError
