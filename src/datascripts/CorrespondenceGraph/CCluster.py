__author__ = 'thodoris'

from bitarray import bitarray
from statsmodels.distributions.empirical_distribution import ECDF
import numpy as np

class CCluster:

    def __init__(self, id, entities, topics):
        self._id = id
        self._entities = set([])
        for e in entities:
            self._entities.add(e)
        self._topics = topics
        self._qualManager = QualityManager(self._id)
        self._srcNames = {}


    def registerSource(self,newSource):
        if newSource.id() not in self._srcNames:
            self._srcNames[newSource.id()] = newSource.uri()
        self._qualManager.registerSource(newSource)

    def registerEvent(self,sourceId,evId):
        self._qualManager.registerEvent(sourceId,evId)

    def registerDelay(self,sourceId,delay):
        self._qualManager.registerDelay(sourceId,delay)

    def registerBias(self,sourceId, polarity, subjectivity):
        self._qualManager.registerBias(sourceId, polarity, subjectivity)

    def id(self):
        return self._id

    def entities(self):
        return self._entities

    def topics(self):
        return self._topics

    def sources(self):
        return self._srcNames.keys()

    def getEvents(self):
        return self._qualManager.events()

    def genQualityProfile(self):
        self._qualManager.buildQualityProfiles()

    def genPricingProfile(self):
        self._qualManager.buildPricingProfiles()

    def printClusterSummary(self,entNameMap,topNameMap):
        entityNames = [entNameMap[e] for e in self._entities]
        topicNames = [topNameMap[e] for e in self._topics]
        print "Cluster ",self._id," content summary..."
        print "Entities: ", " ".join(entityNames)
        print "Topic: ", " ".join(topicNames)
        print "Total events:",len(self._qualManager._events)

    def printCovSummary(self):
        print "Cluster ",self._id," coverage summary..."
        coverages = self._qualManager.srcCoverage()
        for sid in coverages:
            print self._srcNames[sid], coverages[sid]

    def getSrcContent(self,srcId):
        return self._qualManager.getSrcBitArray(srcId)

    def getSrcBias(self, srcId):
        return self._qualManager.getSrcBias(srcId)

    def getSrcDelayedCov(self,srcId,delay):
        return self._qualManager.getSrcDelayedCov(srcId,delay)

    def getSrcCoverage(self,srcId):
        return self._qualManager.getSrcCoverage(srcId)

class QualityManager:

    def __init__(self,cClusterId):
        self._cclusterId = cClusterId
        self._srcIdToSrc = {}
        self._srcEvents = {}
        self._srcDelays = {}
        self._srcPolarity = {}
        self._srcSubjectivity = {}
        self._events = {}
        self._nextEventId = 0
        self._qualityProfiles = {}

        self._srcBitArrays = {}
        self._srcCoverage = {}
        self._srcDelayECDF = {}
        self._srcAvgDelay = {}
        self._srcBias = {}


    def srcCoverage(self):
        return self._srcCoverage

    def registerSource(self, newSource):
        if newSource.id() not in self._srcIdToSrc:
            self._srcIdToSrc[newSource.id()] = newSource
            self._srcEvents[newSource.id()] = set([])
            self._srcDelays[newSource.id()] = []
            self._srcPolarity[newSource.id()] = []
            self._srcSubjectivity[newSource.id()] = []


    def registerEvent(self,sourceId,evId):
        if evId not in self._events:
            self._events[evId] = self._nextEventId
            self._nextEventId += 1

        self._srcEvents[sourceId].add(self._events[evId])

    def registerDelay(self,sourceId,delay):
        self._srcDelays[sourceId].append(delay)

    def registerBias(self,sourceId,polarity, subjectivity):
        self._srcPolarity[sourceId].append(polarity)
        self._srcSubjectivity[sourceId].append(subjectivity)

    def buildQualityProfiles(self):
        # build bitarrays for each source
        totalLen = len(self._events)
        for srcId in self._srcEvents:
            self._srcBitArrays[srcId] = totalLen*bitarray('0')
            for i in self._srcEvents[srcId]:
                self._srcBitArrays[srcId][i] = '1'

            # build coverage profile
            self._srcCoverage[srcId] = float(self._srcBitArrays[srcId].count())/float(totalLen)

            # build delay profile
            # fit Kaplan-Meier empirical distribution
            self._srcDelayECDF[srcId] = ECDF(self._srcDelays[srcId])
            self._srcAvgDelay[srcId] = np.mean(self._srcDelay[srcId])

            # build bias profile
            self._srcBias[srcId] = {}
            self._srcBias[srcId]['polarity'] = np.mean(self._srcPolarity[srcId])
            self._srcBias[srcId]['subjectivity'] = np.mean(self._srcSubjectivity[srcId])
            self._srcBias[srcId]['total'] = float(len(self._srcPolarity[srcId]))

    def buildPricingProfiles(self):
        for srcId in self._srcIdToSrc:
            srcCov = self._srcCoverage[srcId]
            srcAvgDelay = self._srcAvgDelay[srcId]
            srcEvents = float(len(self._srcEvents[srcId]))
            self._srcIdToSrc[srcId].updateCost(srcCov,srcAvgDelay,srcEvents)

    def getSrcCoverage(self,srcId):
        if srcId in self._srcCoverage:
            return self._srcCoverage[srcId]
        else:
            return 0.0

    def getSrcDelayDistr(self,srcId,value):
        return self._srcDelayECDF[srcId](value)

    def getSrcBias(self,srcId):
        if srcId in self._srcBias:
            return self._srcBias[srcId]
        else:
            return None

    def getSrcDelayedCov(self,srcId,delay):
        if srcId not in self._srcDelayECDF:
            return 0.0
        else:
            return self._srcDelayECDF[srcId](delay)*self._srcCoverage[srcId]

    def events(self):
        return float(len(self._events))

    def getSrcAvgDelay(self,srcId):
        return self._srcAvgDelay[srcId]

    def getSrcBitArray(self, srcId):
        if srcId in self._srcBitArrays:
            return self._srcBitArrays[srcId]
        else:
            return None









