__author__ = 'thodoris'


class CostFunction:

    def __init__(self, type):
        self._costType = type

    def compute(self, selectedSources):
        return len(selectedSources)