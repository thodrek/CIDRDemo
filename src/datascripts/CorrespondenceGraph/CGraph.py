__author__ = 'thodoris'

from ClusterManager import ClusterManager
from CCluster import CCluster
from fp_growth import find_frequent_itemsets
from Source import Source
import sys
from whoosh.index import create_in
from whoosh.fields import *
from whoosh import qparser
import os
import re

class CGraph:
    def __init__(self):
        self._Manager = ClusterManager()
        self._cEntRefToName = {}
        self._cTopicToName = {}
        self._sources = {}

    def entToName(self,cRef):
        return self._cEntRefToName[cRef]

    def topToName(self,topicRef):
        return self._cTopicToName[topicRef]

    def manager(self):
        return self._Manager

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
                        self._cEntRefToName[e['cRef']] = e['name']
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



class QueryEngine:

    def __init__(self, indexDir, cGraph):

        if not os.path.exists(indexDir):
            os.mkdir(indexDir)
        self._schema = Schema(cid=ID(stored=True), entities=TEXT(spelling=True), topic=TEXT(spelling=True))
        self._index = create_in("/tmp/index",self._schema)
        self._cGraph = cGraph
        self._searcher = self._index.searcher()
        self._parser = qparser.MultifieldParser(["entities", "topic"], schema=self._index.schema)

    def generateEntityString(self, cluster):
        entityNames = [self._cGraph.entToName(e) for e in cluster.entities()]
        if len(entityNames) == 0:
            entityString = '__None'
        else:
            entityString = ' '.join(entityNames)
        return unicode(entityString)

    def generateTopicString(self, cluster):
        topicNames = [self._cGraph.topToName(e) for e in cluster.topics()]
        topicString = ' '.join(topicNames)
        return unicode(topicString)

    def generateIndex(self):
        c_processed = 0.0
        total_entries = float(len(self._cGraph.manager().clusters()))
        # initialize writer
        writer = self._index.writer()
        clusters = self._cGraph.manager().clusters()
        for cid in clusters:
            c = clusters[cid]
            cid = unicode(cid)
            entities = self.generateEntityString(c)
            topic = self.generateTopicString(c)
            writer.add_document(cid=cid,entities=entities,topic=topic)
            # update progress output
            c_processed += 1.0
            progress = c_processed*100.0/total_entries
            sys.stdout.write("Generating c-cluster index... Progress: %10.2f%% (%d out of %d)   \r" % (progress,c_processed,total_entries))
            sys.stdout.flush()
        writer.commit()

    def processQuery(self,queryString):
        # validate query format
        try:
            found = re.search("entities:",queryString).group(0)
        except AttributeError:
            queryString += "entities:__None"


        # parse query
        q = self._parser(queryString)

        # check query for misspelled words
        corrected = self._searcher.correct_query(q,queryString)
        results = self._searcher.search(corrected.query)
        outClusterIds = []
        for r in results:
            outClusterIds.append(r['cid'])
        return outClusterIds





