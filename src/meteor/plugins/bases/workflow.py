"""
.. module: meteor.plugins.bases.workflow
    :platform: Unix
    :copyright: (c) 2024 by MeteorFlow, see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kyle Tran <kyletran101.work@gmail.com>
"""
from meteor.plugins.base import Plugin


class WorkflowPlugin(Plugin):
    type = "workflow"

    def get_instance(self, workflow_id: str, instance_id: str, **kwargs):
        raise NotImplementedError

    def run(self, workflow_id: str, params: dict, **kwargs):
        raise NotImplementedError
