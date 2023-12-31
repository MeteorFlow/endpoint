"""
.. module: meteor.plugins.bases.storage
    :platform: Unix
    :copyright: (c) 2024 by MeteorFlow, see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kyle Tran <kyletran101.work@gmail.com>
"""
from meteor.plugins.base import Plugin


class StoragePlugin(Plugin):
    type = "storage"

    def get(self, **kwargs):
        raise NotImplementedError

    def create(self, items, **kwargs):
        raise NotImplementedError

    def update(self, items, **kwargs):
        raise NotImplementedError

    def delete(self, items, **kwargs):
        raise NotImplementedError

    def list(self, **kwargs):
        raise NotImplementedError

    def add_participant(self, items, **kwargs):
        raise NotImplementedError

    def remove_participant(self, items, **kwargs):
        raise NotImplementedError

    def open(self, **kwargs):
        raise NotImplementedError

    def mark_readonly(self, folder_id: str, **kwargs):
        raise NotImplementedError

    def add_file(self, **kwargs):
        raise NotImplementedError

    def delete_file(self, **kwargs):
        raise NotImplementedError

    def move_file(self, **kwargs):
        raise NotImplementedError

    def list_files(self, **kwargs):
        raise NotImplementedError
