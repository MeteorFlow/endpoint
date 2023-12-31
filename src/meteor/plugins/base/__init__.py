"""
.. module: meteor.plugins.base
    :platform: Unix
    :copyright: (c) 2024 by MeteorFlow, see AUTHORS for more
    :license: Apache, see LICENSE for more details.

.. moduleauthor:: Kyle Tran <kyletran101.work@gmail.com>
"""
from __future__ import absolute_import, print_function

from meteor.plugins.base.manager import PluginManager
from meteor.plugins.base.v1 import *  # noqa

plugins = PluginManager()
register = plugins.register
unregister = plugins.unregister
