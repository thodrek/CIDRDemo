__author__ = 'thodoris'

from CCluster import CCluster

class ClusterManager:

    def __init__(self):
        self._entitiesToClusters = {}
        self._topicsToClusters = {}
        self._nextId = 0
        self._cClusters = {}


    def addCCluster(self,cCluster):
        cCluster.assignId(self._nextId)
        self._cClusters[cCluster.id] = cCluster
        self._nextId += 1

        # update entity index with new ccluster
        for e in cCluster.entities():
            if e not in self._entitiesToClusters:
                self._entitiesToClusters[e] = set([])
            self._entitiesToClusters[e].add(ccluster.id())

        # update topics index with new ccluster
        for t in cCluster.topics():
            if t not in self._topicsToClusters:
                self._topicsToClusters[t] = set([])
            self._topicsToClusters[t].add(cCluster.id())

    def assignSource(self, entities, topic, source):
        # find relevant c-clusters
        relevantClusters = self._topicsToClusters[topic]
        for e in entities:
            relevantClusters &= self._entitiesToClusters[e]
        # assign source
        for c in relevantClusters:
            c.assigneSource(source)

    def totalClusters(self):
        return self._nextId


    def evaluateQuery(self,query):
        return


