__author__ = 'thodoris'


class CostFunction:

    def __init__(self, type):
        self._costType = type

    def fixedCost(self,selectedSources):
        return len(selectedSources)

    def srcSpecificCost(self,selectedSources):
        totalCost = 0.0
        return totalCost

    def compute(self, selectedSources):
        if self._costType == "fixed":
            return self.fixedCost(selectedSources)
        elif self._costType == "specific":
            return self.srcSpecificCost(selectedSources)
        else:
            return self.fixedCost(selectedSources)
