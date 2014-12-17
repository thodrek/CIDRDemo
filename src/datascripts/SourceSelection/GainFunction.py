__author__ = 'thodoris'

import Metrics

class GainFunction:

    def __init__(self, weights):
        self._weights = weights

    def covGain(self,cov):
        return cov

    def timeGain(self,delayIntervals, delayProbs):
        return 1.0

    def biasGain(selfself,polarity, subjectivity):
        return 1.0

    def compute(self, selectedSources, activeClusters):
        cov = 0.0
        totalGain = 0.0
        if self._weights['cov'] > 0.0:
            cov = Metrics.coverage(selectedSources,activeClusters)
            totalGain += self._weights['cov']*self.covGain(cov)

        if self._weights['time'] > 0.0:
            delayIntervals, delayProbs = Metrics.timeliness(selectedSources,activeClusters)
            totalGain += self._weights['time']*self.timeGain(delayIntervals,delayProbs)

        if self._weights['bias'] > 0.0:
            polarity, subjectivity = Metrics.bias(selectedSources,activeClusters)
            totalGain += self._weights['bias']*self.timeGain(polarity,subjectivity)

        return totalGain
