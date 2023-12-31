"""
.. module: meteor.plugins.bases.oncall
    :platform: Unix
    :copyright: (c) 2024 by MeteorFlow, see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kyle Tran <kyletran101.work@gmail.com>
"""
from meteor.plugins.base import Plugin


class OncallPlugin(Plugin):
    type = "oncall"

    def get(self, service_id: str, **kwargs):
        raise NotImplementedError

    def page(
        self,
        service_id: str,
        incident_name: str,
        incident_title: str,
        incident_description: str,
        **kwargs,
    ):
        raise NotImplementedError
