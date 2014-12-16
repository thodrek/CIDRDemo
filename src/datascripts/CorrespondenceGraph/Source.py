__author__ = 'thodoris'


class Source:

    def __init__(self,sourceId,sourceUri):
        self._id = sourceId
        self._uri = sourceUri
        self._topics = {}
        self._entities = {}

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

    def id(self):
        return self._id

    def uri(self):
        return self._uri

    def topics(self):
        return self._topics.keys()

    def entities(self):
        return self._entities.keys()