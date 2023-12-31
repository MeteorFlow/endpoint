"""
.. module: meteor.plugins.bases.ticket
    :platform: Unix
    :copyright: (c) 2024 by MeteorFlow, see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kyle Tran <kyletran101.work@gmail.com>
"""
from meteor.plugins.base import Plugin


class TicketPlugin(Plugin):
    type = "ticket"

    def create(self, ticket_id, **kwargs):
        raise NotImplementedError

    def update(self, ticket_id, **kwargs):
        raise NotImplementedError

    def delete(self, ticket_id, **kwargs):
        raise NotImplementedError
