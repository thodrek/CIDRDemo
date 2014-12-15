__author__ = 'thodoris'

from CCluster import CCluster

class ClusterManager:

    def __init__(self):
        self._entitiesToClusters = {}
        self._topicsToClusters = {}
        self._nextId = 0
        self._cClusters = {}
        self._sources = {}


    def addCCluster(self, entities, topics):
        cCluster = CCluster(self._nextId,entities,topics)
        self._cClusters[cCluster.id()] = cCluster
        self._nextId += 1

        # update entity index with new ccluster
        for e in cCluster.entities():
            if e not in self._entitiesToClusters:
                self._entitiesToClusters[e] = set([])
            self._entitiesToClusters[e].add(cCluster.id())

        # update topics index with new ccluster
        for t in cCluster.topics():
            if t not in self._topicsToClusters:
                self._topicsToClusters[t] = set([])
            self._topicsToClusters[t].add(cCluster.id())

    def updateSourceEventInfo(self, entities, topic, source, evId, delay):
        # find relevant c-clusters
        candidateClusters = self._topicsToClusters[topic]

        for c in candidateClusters:
            if entities.issuperset(self._cClusters[c].entities()):
                self._cClusters[c].registerSource(source)
                self._cClusters[c].registerEvent(source.id(),evId)
                self._cClusters[c].registerDelay(source.id(),delay)


    def totalClusters(self):
        return self._nextId


    def buildQualityProfiles(self):
        for cKey in self._cClusters:
            self._cClusters[cKey].genQualityProfile()

