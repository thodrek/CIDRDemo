__author__ = 'thodoris'

from ClusterManager import ClusterManager
from CCluster import CCluster
from fp_growth import find_frequent_itemsets
from Source import Source
import sys

class CGraph:
    def __init__(self):
        self._Manager = ClusterManager()
        self._cEntRefToName = {}
        self._cTopicToName = {}
        self._sources = {}

    def generate(self,inputData):
        print "Generating correspondence graph...\n"
        # find total entries
        total_entries = 0.0
        for topicRef in inputData:
            total_entries += float(2.0*len(inputData[topicRef]['articles']))

        # inputData: articles partitioned per topic, associated with entities, sources and associated with events
        entries_processed = 0.0
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
                        self._cEntRefToName[e['cRef']] = []
                    self._cEntRefToName[e['cRef']].append(e['name'])
                    newTrans.add(e['cRef'])

                transactions.append(newTrans)

                # update progress output
                entries_processed += 1.0
                progress = entries_processed*100.0/total_entries
                sys.stdout.write("Generating graph... Progress: %10.2f%% (%d out of %d)   \r" % (progress,entries_processed,total_entries))
                sys.stdout.flush()

            # frequent entityset mining
            entitysets = find_frequent_itemsets(transactions, 5, include_support=True)

            # iterate over entity sets and form valid sets
            validSets = []
            for (entityset, support) in entitysets:
                validSets.append((support,set(entityset)))

                # create c-cluster based on entity set and topic and add it to manager

                self._Manager.addCCluster(entityset,set([topicRef]))

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
                    src = self._sources[srcId]

                # update source topic and entity information
                src.addTopics(set([topicRef]))
                src.addEntities(artEntities)

                # update c-clusters
                evId = ar['eventUri']
                delay = ar['delay']
                self._Manager.updateSourceEventInfo(artEntities, topicRef,src,evId,delay)

                # update progress output
                entries_processed += 1.0
                progress = entries_processed*100.0/total_entries
                sys.stdout.write("Generating graph... Progress: %10.2f%% (%d out of %d)   \r" % (progress,entries_processed,total_entries))
                sys.stdout.flush()
        print "\n"


    def summary(self):
        print ("The graph contains %d c-clusters in total." % self._Manager.totalClusters())
        print ("The graph contains %d topics in total." % len(self._cTopicToName))
        print ("The graph contains %d entities in total." % len(self._cEntRefToName))
        print ("The graph contains %d sources in total." % len(self._sources))


    def manager(self):
        return self._Manager




