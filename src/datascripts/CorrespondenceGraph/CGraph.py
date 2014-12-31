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
from textblob import TextBlob
import json
import heapq
import csv
from SourceSelection import Metrics

class CGraph:
    def __init__(self):
        self._Manager = ClusterManager(self)
        self._cEntRefToName = {}
        self._cTopicToName = {}
        self._sources = {}

    def entToName(self,cRef):
        return self._cEntRefToName[cRef]

    def topToName(self,topicRef):
        return self._cTopicToName[topicRef]

    def manager(self):
        return self._Manager

    def getSourceName(self,srcId):
        return self._Manager.getSrcName(srcId)

    def getSources(self):
        return self._sources

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
                    eCanName = e['name']
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
                src.addEvent(ar['eventUri'])

                # update c-clusters
                evId = ar['eventUri']
                delay = ar['delay']
                arBody = TextBlob(ar['body'])
                arTitle = TextBlob(ar['title'])

                # find article bias
                polarity = arTitle.sentiment.polarity
                if abs(polarity) > abs(arBody.sentiment.polarity):
                    polarity = arBody.sentiment.polarity

                subjectivity = arTitle.sentiment.subjectivity
                if abs(subjectivity) > abs(arBody.sentiment.subjectivity):
                    subjectivity = arTitle.sentiment.subjectivity

                # send info to manager
                self._Manager.updateSourceEventInfo(artEntities, topicRef,src,evId,delay,polarity,subjectivity)

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

    def processQuery(self,queryString, limit):
        # initialize searcher
        searcher = self._index.searcher()

        # analyze query format
        parser = None
        if "entities:" in queryString and "topic:" in queryString:
            parser = qparser.MultifieldParser(["entities", "topic"], schema=self._index.schema)
        elif "entities:" in queryString and "topic:" not in queryString:
            parser = qparser.QueryParser("entities", schema=self._index.schema)
        elif "entities:" not in queryString and "topic:" in queryString:
            parser = qparser.QueryParser("topic", schema=self._index.schema)
        else:
            parser = None

        if parser == None:
            return []
        # parse query
        q = parser.parse(unicode(queryString))

        # check query for misspelled words
        corrected = searcher.correct_query(q,queryString)
        if corrected.query != q:
            status = "Did you mean: "+corrected.string
        else:
            status = "OK"
        results = searcher.search(q, limit=limit)
        outClusterIds = []
        for r in results:
            outClusterIds.append(int(r['cid']))
        return outClusterIds, status



class DataFormater:

    def __init__(self, cgraph):
        self._cgraph = cgraph


    def cgraphExploration(self, clusterIds):
        result = {}
        result['nodes'] = []
        result['links'] = []

        nodes = {}
        nodeNames = []
        nid = 0
        # populate nodes
        for cid in clusterIds:
            cTopic = list(self._cgraph.manager().clusters()[cid].topics())
            cTopic = cTopic[0].split('/')[-1]
            clusterName = "Cluster "+str(cid)+", Topic: "+cTopic
            if clusterName not in nodes:
                nodes[clusterName] = nid
                nodeNames.append(clusterName)
                nid += 1
            entityWeights = self._cgraph.manager().clusterEntityWeights()[cid]
            for eid in entityWeights:
                eName = self._cgraph.entToName(eid)
                eName = eName.replace("the ","")
                if eName not in nodes:
                    nodes[eName] = nid
                    nodeNames.append(eName)
                    nid += 1
            srcWeights = self._cgraph.manager().clusterSourceWeights()[cid]
            for sid in srcWeights:
                sName = self._cgraph.getSourceName(sid)
                if sName not in nodes:
                    nodeNames.append(sName)
                    nodes[sName] = nid
                    nid += 1

        edges = {}
        # populate edges
        for cid in clusterIds:
            cTopic = list(self._cgraph.manager().clusters()[cid].topics())
            cTopic = cTopic[0].split('/')[-1]
            clusterName = "Cluster "+str(cid)+", Topic: "+cTopic
            entityWeights = self._cgraph.manager().clusterEntityWeights()[cid]
            for eid in entityWeights:
                eName = self._cgraph.entToName(eid)
                eName = eName.replace("the ","")
                linkWeight = entityWeights[eid]
                edge = (eName,clusterName)
                if edge not in edges:
                    edges[edge] = 0.0
                edges[edge] += linkWeight
            srcWeights = self._cgraph.manager().clusterSourceWeights()[cid]
            for sid in srcWeights:
                sName = self._cgraph.getSourceName(sid)
                linkWeight = srcWeights[sid]
                edge = (clusterName,sName)
                if edge not in edges:
                    edges[edge] = 0.0
                edges[edge] += linkWeight

        # construct result
        for n in nodeNames:
            result['nodes'].append({"name":n})

        for e in edges:
            result['links'].append({"source":nodes[e[0]], "target":nodes[e[1]], "value":edges[e]})

        # convert result to json and return
        return json.dumps(result)


    def cgraphExplorationOverlaps(self, clusterIds, srcs):
        activeClusters = set([])
        for cid in clusterIds:
            activeClusters.add(self._cgraph.manager().clusters()[cid])

        singleCoverage = {}

        for srcOut in srcs:
            for srcIn in srcs:
                sNameOut = self._cgraph.getSourceName(srcOut)
                sNameIn = self._cgraph.getSourceName(srcIn)
                selection = set([srcOut, srcIn])
                selectionKey = sNameOut+ ", "+ sNameIn
                coverage = Metrics.coverage(selection,activeClusters)
                if sNameIn == sNameOut:
                    singleCoverage[sNameIn] = coverage
                print selectionKey, coverage

        topSrcs = sorted(singleCoverage.items(), key=lambda x: (-x[1], x[0]))
        print "\n"
        for r in topSrcs:
            print r[0], r[1]




    def cgraphExplorationTest(self, clusterIds):
        result = {}
        result['nodes'] = []
        result['links'] = []
        srcsNameToId = {}
        srcs = set([])

        # find edges for clusters
        edges = {}
        # find all edges
        for cid in clusterIds:
            cTopic = list(self._cgraph.manager().clusters()[cid].topics())
            cTopic = cTopic[0].split('/')[-1]
            #clusterName = "Cluster "+str(cid)+", Topic: "+cTopic
            clusterName = "C_"+str(cid)+"\n Topic: "+cTopic
            edges[clusterName] = {}
            edges[clusterName]['entities'] = {}
            edges[clusterName]['sources'] = {}
            entityWeights = self._cgraph.manager().clusterEntityWeights()[cid]
            for eid in entityWeights:
                eName = self._cgraph.entToName(eid)
                eName = eName.replace("the ","")
                linkWeight = entityWeights[eid]
                edge = (eName,clusterName)
                if edge not in edges[clusterName]['entities']:
                    edges[clusterName]['entities'][edge] = 0.0
                edges[clusterName]['entities'][edge] += linkWeight
            srcWeights = self._cgraph.manager().clusterSourceWeights()[cid]
            for sid in srcWeights:
                sName = self._cgraph.getSourceName(sid)
                srcsNameToId[sName] = sid
                linkWeight = srcWeights[sid]
                edge = (clusterName,sName)
                if edge not in edges[clusterName]['sources']:
                    edges[clusterName]['sources'][edge] = 0.0
                edges[clusterName]['sources'][edge] += linkWeight

        # for each cluster keep top 5 entities and top 5 sources
        nodes = {}
        nid = 0
        for cid in clusterIds:

            # grab cluster info
            cTopic = list(self._cgraph.manager().clusters()[cid].topics())
            cTopic = cTopic[0].split('/')[-1]
            #clusterName = "Cluster "+str(cid)+", Topic: "+cTopic
            clusterName = "C_"+str(cid)+"\n Topic: "+cTopic
            nodes[clusterName] = nid
            nid += 1
            cNodeId = nodes[clusterName]

            # top entity edges
            entityEdges = edges[clusterName]['entities']
            top5entityEdges = heapq.nlargest(5,entityEdges,entityEdges.get)
            for edge in top5entityEdges:
                eName = edge[0]
                if eName in nodes:
                    eNodeId = nodes[eName]
                else:
                    eNodeId = nid
                    nodes[eName] = eNodeId
                    nid += 1
                result['links'].append({"source":eNodeId, "target":cNodeId, "value":edges[clusterName]['entities'][edge]})

            # top source edges
            sourceEdges = edges[clusterName]['sources']
            top5sourceEdges = heapq.nlargest(5,sourceEdges,sourceEdges.get)
            for edge in top5sourceEdges:
                sName = edge[1]
                srcs.add(srcsNameToId[sName])
                if sName in nodes:
                    sNodeId = nodes[sName]
                else:
                    sNodeId = nid
                    nodes[sName] = sNodeId
                    nid += 1
                result['links'].append({"source":cNodeId, "target":sNodeId, "value":edges[clusterName]['sources'][edge]})


        # add node info
        orderedNodes = [k for k, v in sorted(nodes.iteritems(), key=lambda (k,v): (v,k))]
        for n in orderedNodes:
            result['nodes'].append({"name":n})

        # print coverage and pairwise coverages
        print "\n"
        self.cgraphExplorationOverlaps(clusterIds,srcs)
        print "\n"

        # convert result to json and return
        return json.dumps(result)

    def selectionJSON(self,paretopoints, dominatedPoints):
        results = []
        for p in paretopoints:
            values = paretopoints[p]
            results.append({"Point Type":"pareto", "coverage Gain":str(round(values[0],2)),"Timeliness Gain":str(round(values[1],2)), "Bias Gain":str(round(values[2],2)), "Cost":str(round(values[3],2))})
        for p in dominatedPoints:
            values = dominatedPoints[p]
            results.append({"Point Type":"dominated", "coverage gain":str(round(values[0],2)),"Timeliness Gain":str(round(values[1],2)), "Bias Gain":str(round(values[2],2)), "Cost":str(round(values[3],2))})
        return json.dumps(results)

    def selectionCSV(self,paretopoints, dominatedPoints):
        filename = "sel.csv"
        with open(filename, 'wb') as csvfile:
            fwriter = csv.writer(csvfile, delimiter=',')
            fwriter.writerow(['id','point type','coverage gain','timeliness gain','bias gain','cost'])
            for p in paretopoints:
                values = paretopoints[p]
                fwriter.writerow([p,'pareto',round(values[0],2),round(values[1],2),round(values[2],2),round(values[3],2)])
            for p in dominatedPoints:
                values = dominatedPoints[p]
                fwriter.writerow([p,'dominated',round(values[0],2),round(values[1],2),round(values[2],2),round(values[3],2)])


