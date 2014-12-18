__author__ = 'thodoris'


class Source:

    def __init__(self,sourceId,sourceUri):
        self._id = sourceId
        self._uri = sourceUri
        self._topics = {}
        self._entities = {}
        self._events = set([])
        self._costValues = []
        self._costWeights = []
        self._totalCost = None

    def addTopics(self,topics):
        for t in topics:
            if t not in self._topics:
                self._topics[t] = 0
            self._topics[t] += 1

    def addEntities(self,entities):
        for e in entities:
            if e not in self._entities:
                self._entities[e] = 0
            self._entities[e] += 1

    def addEvent(self,eid):
        self._events.add(eid)

    def srcProfile(self):
        profile = {}
        profile['topics'] = len(self._topics)
        profile['entities'] = len(self._entities)
        profile['events'] = len(self._events)
        return profile

    def covCost(self,cov):
        if cov < 0.2:
            cost = 10.0 + 10.0*cov
        elif cov >= 0.2 and cov < 0.5:
            cost = 20.0 + 10.0*(cov - 0.2)
        elif cov >= 0.5 and cov < 0.7:
            cost = 40.0 + 10.0*(cov - 0.5)
        elif cov >= 0.7 and cov < 0.8:
            cost = 60.0 + 10.0*(cov - 0.7)
        else:
            cost = 100.0 + 10.0*(cov - 0.8)
        return cost

    def delayCost(self,delay):
        if delay < 10:
            cost = 100
        elif delay >= 10 and delay < 60:
            cost = 80
        elif delay >= 60 and delay < 360:
            cost = 60
        elif delay >= 360 and delay < 1440:
            cost = 50
        elif delay >= 1440 and delay < 2880:
            cost = 20
        else:
            cost = 10
        return cost

    def updateCost(self,cov,delay,events):
        totalCost = self._covCost(cov) + self._delayCost(delay)

        self._costValues.append(totalCost)
        self._costWeights.append(events)

    def computeCost(self):
        if not self._totalCost:
            self._totalCost = 0.0
            totalWeight = 0.0
            for i in range(len(self._costValues)):
                cost = self._costValues[i]
                costWeight = self._costWeights[i]
                self._totalCost += cost*costWeight
                totalWeight += costWeight
            self._totalCost = self._totalCost/totalWeight
        return self._totalCost

    def id(self):
        return self._id

    def uri(self):
        return self._uri

    def topics(self):
        return self._topics.keys()

    def entities(self):
        return self._entities.keys()