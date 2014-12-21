__author__ = 'thodoris'

from CCluster import CCluster
import sys

class ClusterManager:

    def __init__(self,cgraph):
        self._cgraph = cgraph
        self._entitiesToClusters = {}
        self._topicsToClusters = {}
        self._nextId = 0
        self._cClusters = {}
        self._sources = {}
        self._ClusterEntityWeights = {}
        self._ClusterSourceWeights = {}


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

    def updateSourceEventInfo(self, entities, topic, source, evId, delay, polarity, subjectivity):
        # update source info
        self._sources[source.id()] = source.uri()

        # find relevant c-clusters
        candidateClusters = self._topicsToClusters[topic]

        for c in candidateClusters:
            if entities.issuperset(self._cClusters[c].entities()):
                self._cClusters[c].registerSource(source)
                self._cClusters[c].registerEvent(source.id(),evId)
                self._cClusters[c].registerDelay(source.id(),delay)
                self._cClusters[c].registerBias(source.id(), polarity, subjectivity)

                # update cluster-entity weights
                cid = self._cClusters[c].id()
                srcId = source.id()
                entIds = self._cClusters[c].entities()

                # update cluster source weight
                if cid not in self._ClusterSourceWeights:
                    self._ClusterSourceWeights[cid] = {}
                if srcId not in self._ClusterSourceWeights[cid]:
                    self._ClusterSourceWeights[cid][srcId] = 0.0
                self._ClusterSourceWeights[cid][srcId] += 1.0

                # update cluster entity weight
                for eId in entIds:
                    if cid not in self._ClusterEntityWeights:
                        self._ClusterEntityWeights[cid] = {}
                    if eId not in self._ClusterEntityWeights[cid]:
                        self._ClusterEntityWeights[cid][eId] = 0.0
                    self._ClusterSourceWeights[cid][eId] += 1.0

    def totalClusters(self):
        return self._nextId

    def buildQualityProfiles(self):
        c_processed = 0.0
        total_entries = float(len(self._cClusters))
        for cKey in self._cClusters:
            self._cClusters[cKey].genQualityProfile()
            # update progress output
            c_processed += 1.0
            progress = c_processed*100.0/total_entries
            sys.stdout.write("Building quality profiles... Progress: %10.2f%% (%d out of %d)   \r" % (progress,c_processed,total_entries))
            sys.stdout.flush()

    def buildPricingProfiles(self):
        c_processed = 0.0
        total_entries = float(len(self._cClusters))
        for cKey in self._cClusters:
            self._cClusters[cKey].genPricingProfile()
            # update progress output
            c_processed += 1.0
            progress = c_processed*100.0/total_entries
            sys.stdout.write("Building pricing profiles... Progress: %10.2f%% (%d out of %d)   \r" % (progress,c_processed,total_entries))
            sys.stdout.flush()

    def clusters(self):
        return self._cClusters

    def getSrcName(self,srcId):
        return self._sources[srcId]



