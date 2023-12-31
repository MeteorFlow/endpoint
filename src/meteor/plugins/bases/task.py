"""
.. module: meteor.plugins.bases.task
    :platform: Unix
    :copyright: (c) 2024 by MeteorFlow, see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kyle Tran <kyletran101.work@gmail.com>
"""
from meteor.plugins.base import Plugin


class TaskPlugin(Plugin):
    type = "task"

    def get(self, **kwargs):
        raise NotImplementedError

    def create(self, **kwargs):
        raise NotImplementedError

    def delete(self, **kwargs):
        raise NotImplementedError

    def list(self, **kwargs):
        raise NotImplementedError

    def resolve(self, **kwargs):
        raise NotImplementedError
