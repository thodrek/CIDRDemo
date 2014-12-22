__author__ = 'thodoris'


import sys
import argparse
import json

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.twisted.websocket import WebSocketServerFactory, \
                                       WebSocketServerProtocol

from autobahn.twisted.resource import WebSocketResource, \
                                      HTTPChannelHixie76Aware

from CorrespondenceGraph import CGraph
from SourceSelection import LocalSearch
from SourceSelection import GainFunction
from SourceSelection import CostFunction
from Utilities import DataLoader


class CGraphServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("WebSocket connection request: {}".format(request))

    def onMessage(self, payload, isBinary):
        if not isBinary:
            query = payload.decode('utf8')
            print "Received ", query
            if "_clusters:" in query:
                query = query.replace("_clusters:","")
                payload = self.factory.retrieveClusters(str(query))
                self.sendMessage(payload,isBinary=False)
            if "_selection:" in query:
                query = query.replace("_selection:","")
                payload = self.factory.retrieveSelectedSources(str(query))
                self.sendMessage(payload,isBinary=False)


class CGraphFactory(WebSocketServerFactory):

    protocol = CGraphServerProtocol

    def __init__(self, wsuri, debug, dataDir):
        WebSocketServerFactory.__init__(self, wsuri, debug=debug, debugCodePaths=debug)
        self._loader = DataLoader.DataLoader(dataDir)
        self._loader.generateInput()
        self._cgraph = CGraph.CGraph()
        self._cgraph.generate(self._loader.getInput())
        self._cgraph.summary()

        print "Start building quality profiles..."
        self._cgraph.manager().buildQualityProfiles()
        print "\nDONE"

        print "Build query engine"
        self._qEngine = CGraph.QueryEngine("/tmp/index",self._cgraph)
        self._qEngine.generateIndex()
        print "\nDONE"

        print "Build data former"
        self._dataformater = CGraph.DataFormater(self._cgraph)
        print "\nDONE"

    def retrieveClusters(self,qString):
        print qString
        qRes, status = self._qEngine.processQuery(qString)
        if status == "OK":
            if len(qRes) == 0:
                payload = "No results found!"
            else:
                # Format result to json
                payload = self._dataformater.cgraphExploration(qRes)
        else:
            tmpStr = str(status)
            tmpStr = tmpStr.replace("entities:", "")
            tmpStr = tmpStr.replace("topic:", "")
            payload = tmpStr
        return payload

    def retrieveSelectedSources(self,qString):
        payload = "Not supported yet!"
        return payload


def main():
    # Read input arguments
    print "Reading input args...",
    parser = argparse.ArgumentParser(description='Please use script as "python server.py -i <input_files_dir>. -d')
    parser.add_argument('-i','--input',help="Specifies input directory.",required=True)
    parser.add_argument('-d','--debug',help="Debug option.",required=False)
    args = vars(parser.parse_args())
    inputDir = args['input']
    if 'debug' in args:
        debug = True
    else:
        debug = False
    print "DONE."

    print "Initalizing server..."
    factory = CGraphFactory("ws://localhost:8080", debug,inputDir)
    resource = WebSocketResource(factory)
    ## we server static files under "/" ..
    root = File(".")

    ## and our WebSocket server under "/ws"
    root.putChild("ws", resource)

    ## both under one Twisted Web Site
    site = Site(root)
    reactor.listenTCP(8080, site)
    reactor.run()

if __name__ == '__main__':
    main()