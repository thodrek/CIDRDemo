__author__ = 'thodoris'


class Source:

    def __init__(self,sourceId):
        self._id = sourceId
        self._topics = {}
        self._entities = {}

    def id(self):
        return self._id

    def topics(self):
        return self._topics.keys()

    def entities(self):
        return self._entities.keys()