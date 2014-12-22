__author__ = 'thodoris'


class CostFunction:

    def __init__(self, type, sourceIndex):
        self._costType = type
        self._srcIndex = sourceIndex

    def fixedCost(self,selectedSources):
        return len(selectedSources)

    def srcSpecificCost(self,selectedSources):
        totalCost = 0.0
        for srcId in selectedSources:
            totalCost += self._srcIndex[srcId].computeCost()
        return totalCost

    def compute(self, selectedSources):
        if self._costType == "fixed":
            return self.fixedCost(selectedSources)
        elif self._costType == "specific":
            return self.srcSpecificCost(selectedSources)
        else:
            return self.fixedCost(selectedSources)
