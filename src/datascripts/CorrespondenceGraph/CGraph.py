__author__ = 'thodoris'

from ClusterManager import ClusterManager
from CCluster import CCluster
from fp_growth import find_frequent_itemsets

class CGraph:
    def __init__(self):
        self._Manager = ClusterManager()
        self._cEntRefToName = {}
        self._cTopicToName = {}

    def addCCluster(self,cCluster):
        self._Manager.addCCluster(cCluster)

    def generate(self,inputData):
        # inputData: articles partitioned per topic, associated with entities, sources and associated with events
        for topic in inputData:
            # update topic reference to name map
            if topic['namedRef'] not in self.cTopicToName:
                self.cTopicToName[topic['namedRef']] = topic['name']

            # initialize article transactions
            transactions = []

            # initialize entity to artic

            # populate article transactions
            for ar in inputData[topic]:
                newTrans = set([])

                for e in ar['entities']:
                    # update entity reference to name map
                    if e['cRef'] not in self.cEntRefToName:
                        self.cEntRefToName = []
                    self.cEntRefToName.append(e['name'])
                    newTrans.add(e['cRef'])

                transactions.add(newTrans)

            # frequent entityset mining
            entitysets = find_frequent_itemsets(transactions, 5, include_support=True)

            # iterate over entity sets and form valid sets
            validSets = []
            for (entityset, support) in entitysets:
                validSets.append((support,set(entityset)))

                # create c-cluster based on entity set and topic
                newcluster = CCluster(set(entityset),set([topic['namedRef']]))

                # add c-cluster to manager
                self.addCCluster(newcluster)

            # iterate over articles and assign sources to c-clusters


