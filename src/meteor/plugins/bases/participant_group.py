"""
.. module: meteor.plugins.bases.participant_group
    :platform: Unix
    :copyright: (c) 2024 by MeteorFlow, see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kyle Tran <kyletran101.work@gmail.com>
"""
from meteor.plugins.base import Plugin


class ParticipantGroupPlugin(Plugin):
    type = "participant-group"

    def create(self, participants, **kwargs):
        raise NotImplementedError

    def add(self, participant, **kwargs):
        raise NotImplementedError

    def remove(self, participant, **kwargs):
        raise NotImplementedError

    def delete(self, group, **kwargs):
        raise NotImplementedError

    def list(self, group, **kwargs):
        raise NotImplementedError
