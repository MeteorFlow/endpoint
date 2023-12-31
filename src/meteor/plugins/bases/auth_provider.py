"""
.. module: meteor.plugins.bases.application
    :platform: Unix
    :copyright: (c) 2024 by MeteorFlow, see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kyle Tran <kyletran101.work@gmail.com>
"""
from meteor.plugins.base import Plugin
from starlette.requests import Request


class AuthenticationProviderPlugin(Plugin):
    type = "auth-provider"

    def get_current_user(self, request: Request, **kwargs):
        raise NotImplementedError
