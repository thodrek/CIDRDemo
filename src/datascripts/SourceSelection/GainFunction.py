__author__ = 'thodoris'

import Metrics

class GainFunction:

    def __init__(self, type, weights):
        self._type = type
        self._weights = weights

    def compute(self, selectedSources, activeClusters):
        cov = Metrics.coverage(selectedSources,activeClusters)
        return 1000*cov
