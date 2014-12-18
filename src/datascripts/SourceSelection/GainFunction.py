__author__ = 'thodoris'

import Metrics
import numpy as np
import math
from Utilities import functions

class GainFunction:

    def __init__(self, weights):
        self._weights = weights

    def covGain(self,cov):
        return 1000*cov

    def timeGain(self,delayIntervals, delayProbs):
        sample = functions.sampleCDF(delayIntervals,delayProbs,10000)
        # compute average delay, upper and lower bound
        m = np.mean(sample)
        ste = np.std(sample)/math.sqrt(len(sample))
        upper = m + ste*1.96
        lower = m - ste*1.96

        # compute gain based on upper and lower
        gainUpper = 1440.0/upper
        gainLower = 1440.0/lower
        gain = (gainUpper + gainLower)/2.0
        return gain

    def biasGain(selfself,polarity, subjectivity):

        polarityDist = abs(polarity)
        subjectivityDist = abs(subjectivity)
        overallDistance = 0.4*polarityDist + 0.6*subjectivityDist
        gain = 1/(0.001 + overallDistance)
        return gain

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
