"""
.. module: meteor.plugins.bases.signal_enrichment
    :platform: Unix
    :copyright: (c) 2022 by MeteorFlow Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Kyle Tran <kyletran101.work@gmail.com>
"""
from meteor.plugins.base import Plugin


class SignalEnrichmentPlugin(Plugin):
    type = "signal-enrichment"

    def enrich(self, **kwargs):
        raise NotImplementedError
