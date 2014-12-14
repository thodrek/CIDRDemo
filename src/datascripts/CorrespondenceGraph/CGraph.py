__author__ = 'thodoris'

from ClusterManager import ClusterManager
from CCluster import CCluster
from fp_growth import find_frequent_itemsets
from Source import Source

class CGraph:
    def __init__(self):
        self._Manager = ClusterManager()
        self._cEntRefToName = {}
        self._cTopicToName = {}
        self._sources = {}

    def addCCluster(self,cCluster):
        self._Manager.addCCluster(cCluster)

    def generate(self,inputData):
        # inputData: articles partitioned per topic, associated with entities, sources and associated with events
        for topicRef in inputData:
            # get topic
            topic = inputData[topicRef]
            # update topic reference to name map
            if topicRef not in self._cTopicToName:
                self._cTopicToName[topicRef] = topic['name']

            # initialize article transactions
            transactions = []

            # initialize entity to artic

            # populate article transactions
            for ar in topic['articles']:
                newTrans = set([])

                for e in ar['entities']:
                    # update entity reference to name map
                    if e['cRef'] not in self._cEntRefToName:
                        self._cEntRefToName = []
                    self._cEntRefToName.append(e['name'])
                    newTrans.add(e['cRef'])

                transactions.append(newTrans)

            # frequent entityset mining
            entitysets = find_frequent_itemsets(transactions, 5, include_support=True)

            # iterate over entity sets and form valid sets
            validSets = []
            for (entityset, support) in entitysets:
                validSets.append((support,set(entityset)))

                # create c-cluster based on entity set and topic
                newcluster = CCluster(entityset,set([topicRef]))

                # add c-cluster to manager
                self.addCCluster(newcluster)

            # iterate over articles and assign sources to c-clusters
            for ar in topic['articles']:
                # form entity set
                artEntities = set([])

                for e in ar['entities']:
                    # update entity reference to name map
                    artEntities.add(e['cRef'])

                # find source information
                srcId = ar['sourceId']
                srcUri = ar['sourceUri']
                src = None
                if srcId not in self._sources:
                    newSource = Source(srcId,srcUri)
                    self._sources[srcId] = newSource
                    src = newSource
                else:
                    src = self_sources[srcId]

                # update source topic and entity information
                src.addTopics(set([topicRef]))
                src.addEntities(artEntities)

                # update c-clusters
                self._Manager.assignSource(artEntities, topicRef,src)

    def summary(self):
        print ("The graph contains %d c-clusters in total." % self._Manager.totalClusters())
        print ("The graph contains %d topics in total." % len(self._cTopicToName))
        print ("The graph contains %d entities in total." % len(self._cEntRefToName))
        print ("The graph contains %d sources in total." % len(self._sources))




