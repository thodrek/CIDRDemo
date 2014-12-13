__author__ = 'thodoris'

from CCluster import CCluster

class ClusterManager:

    def __init__(self):
        self.entitiesToClusters = {}
        self.topicsToClusters = {}
        self.cclusterIds = 0
        self.cclusters = {}


    def addCCluster(self,entities, topics, sources):
        # create new ccluster
        ccluster =  CCluster(self.cclusterIds, entities, topics, sources)
        self.cclusterIds += 1
        self.cclusterIds[ccluster.id] = ccluster

        # update entity index with new ccluster
        for e in ccluster.entities:
            if e not in self.entitiesToClusters:
                self.entitiesToClusters[e] = set([])
            self.entitiesToClusters[e].add(ccluster.id)

        # update topics index with new ccluster
        for i in ccluster.topics:
            if t not in self.topicsToClusters:
                self.topicsToClusters[t] = set([])
            self.topicsToClusters[t].add(ccluster.id)


    def evaluateQuery(self,query):
        return


