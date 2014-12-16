__author__ = 'thodoris'

from twisted.internet.protocol import Factory
from twisted.internet import reactor, protocol
from CorrespondenceGraph import CGraph
import DataLoader
import argparse


class CGraphApi(protocol.Protocol):

    def __init__(self,cgraph,queryengine):
        self._cgraph = cgraph
        self._queryengine = queryengine

    def connectionMade(self):
        self.transport.write("Please post your query...")

    def dataReceived(self,data):
        print "Received ", data
        qRes = self._queryengine.processQuery(data)
        self.transport.write(qRes)

class CGraphFactory(Factory):

    def __init__(self,dataDir):
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

    def buildProtocol(self, addr):
        return CGraphApi(self._cgraph,self._qEngine)


def main():
    """This runs the protocol on port 8000"""
    # Read input arguments
    print "Reading input args...",
    parser = argparse.ArgumentParser(description='Please use script as "python Server.py -i <input_files_dir>.')
    parser.add_argument('-i','--input',help="Specifies input directory.",required=True)
    args = vars(parser.parse_args())
    inputDir = args['input']
    print "DONE."

    print "Initalizing server..."
    reactor.listenTCP(8000,CGraphFactory(inputDir))
    reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()