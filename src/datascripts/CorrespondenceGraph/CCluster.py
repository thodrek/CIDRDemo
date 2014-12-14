__author__ = 'thodoris'

from SourceQuality import SourceQuality

class CCluster:

    def __init__(self, entities, topics):
        self._id = -1
        self._entities = set([])
        for e in entities:
            self._entities.add(e)
        self._topics = topics
        self._sources = {}
        self._events = set([])
        self._qualityProfiles = {}

    def assignId(self,newId):
        self._id = newId

    def assignSource(self,newSource):
        if newSource.id() not in self._sources:
            self._sources[newSource.id()] = set([])

    def assignEvent(self,sourceId,evId):
        self._events.add(evId)
        self._sources[sourceId].add(evId)

    def id(self):
        return self._id

    def entities(self):
        return self._entities

    def topics(self):
        return self._topics

    def sources(self):
        return self._sources

    def buildQualityProfile(self):
        for srcId in self._sources:
            src = self._sources[srcId]

            # build quality profile
            srcQual = SourceQuality(srcId,src.uri())
            srcCov = float(len(self._sources[srcId]))/float(len(self._events))
            srcQual.setCoverage(srcCov)

            # store quality profile
            self._qualityProfiles[srcId] = srcQual

    def printCoverage(self):
        for srcId in self._qualityProfiles:
            print srcId, self._qualityProfiles[srcId].getCoverage()

