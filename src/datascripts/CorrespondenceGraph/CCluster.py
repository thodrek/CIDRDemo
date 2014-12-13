__author__ = 'thodoris'


class CCluster:

    def __init__(self, entities, topics):
        self._id = -1
        self._entities = entities
        self._topics = topics
        self._sources = set([])

    def assignId(self,newId):
        self._id = newId

    def assignSource(self,newSource):
        self._sources.add(newSource)


    def id(self):
        return self._id

    def entities(self):
        return self._entities

    def topics(self):
        return self._topics

    def sources(self):
        return self._sources
