__author__ = 'thodoris'

from ClusterManager import ClusterManager
from fp_growth import find_frequent_itemsets

class CGraph:
    def __init__(self):
        self.Manager = ClusterManager()
        self.cEntRefToName = {}
        self.cTopicToName = {}


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

            # iterate over entity sets
            for (entityset, support) in entitysets:
                entityset = 



