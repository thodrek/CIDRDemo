__author__ = 'thodoris'

class SourceQuality:

    def __init__(self,srcId,srcUri):
        self._srcId = srcId
        self._srceUri = srcUri
        self._coverage = None

    def setCoverage(self,newCov):
        self._coverage = newCov

    def getCoverage(self):
        return self._coverage