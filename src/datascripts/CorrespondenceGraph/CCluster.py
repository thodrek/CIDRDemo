__author__ = 'thodoris'

from SourceQuality import SourceQuality
from bitarray import bitarray

class CCluster:

    def __init__(self, id, entities, topics):
        self._id = id
        self._entities = set([])
        for e in entities:
            self._entities.add(e)
        self._topics = topics
        self._qualManager = QualityManager(self._id)


    def registerSource(self,newSource):
        self._qualManager.registerSource(newSource)

    def registerEvent(self,sourceId,evId):
        self._qualManager.registerEvent(sourceId,evId)

    def id(self):
        return self._id

    def entities(self):
        return self._entities

    def topics(self):
        return self._topics

    def sources(self):
        return self._sources

    def genQualityProfile(self):
        self._qualManager.buildQualityProfiles()

class QualityManager:

    def __init__(self,cClusterId):
        self._cclusterId = cClusterId
        self._srcIdToSrc = {}
        self._srcEvents = {}
        self._events = {}
        self._nextEventId = 0
        self._qualityProfiles = {}

        self._srcBitArrays = {}
        self._srcCoverage = {}

    def registerSource(self, newSource):
        if newSource.id() not in self._srcIdToSrc:
            self._srcIdToSrc[newSource.id()] = newSource
            self._srcEvents[newSource.id()] = set([])


    def registerEvent(self,sourceId,evId):
        if evId not in self._events:
            self._events[evId] = self._nextEventId
            self._nextEventId += 1

        self._srcEvents[sourceId].add(self._events[evId])

    def buildQualityProfiles(self):
        # build bitarrays for each source
        totalLen = len(self._events)
        for srcId in self._srcEvents:
            self._srcBitArrays[srcId] = totalLen*bitarray('0')
            for i in self._srcEvents[srcId]:
                self._srcBitArrays[srcId][i] = '1'

            # build coverage profile
            self._srcCoverage[srcId] = float(self._srcBitArrays[srcId].count())/float(totalLen)

    def getSrcCoverage(self,srcId):
        return self._srcCoverage[srcId]




