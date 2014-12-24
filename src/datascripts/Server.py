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
from SourceSelection import ParetoFront

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
                query = query.split("&&")
                queryBody = query[0]
                costType = query[1]
                cost = float(query[2])
                queryBody = queryBody.replace("_selection:","")
                reactor.callLater(1,self.selectionResult,(queryBody, costType, cost))
                self.sendMessage("Processing please wait...",isBinary=False)
            if "_profile:" in query:
                query = query.split(":")
                id = int(query[1])
                payload = self.factory.retrieveProfile(id)
                self.sendMessage(payload,isBinary=False)
            if "_sources:" in query:
                query = query.split(":")
                id = int(query[1])
                payload = self.factory.retrieveSourcesProfile(id)
                self.sendMessage(payload,isBinary=False)

    def selectionResult(self, args):
        queryBody, costType, cost = args
        payload = self.factory.retrieveSelectedSources(str(queryBody),costType,cost)
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
        self._costType = "fixed"

        self._selectionCache = {}
        self._selectionCache['paretoPoints'] = None
        self._selectionCache['dominatedPoints'] = None
        self._selectionCache['solutionProfiles'] = None

        print "Start building quality profiles..."
        self._cgraph.manager().buildQualityProfiles()
        print "\nDONE"

        print "Start building pricing profiles..."
        self._cgraph.manager().buildPricingProfiles()
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
        qRes, status = self._qEngine.processQuery(qString,10)
        if status == "OK":
            if len(qRes) == 0:
                payload = "No results found!"
            else:
                # Format result to json
                payload = self._dataformater.cgraphExplorationTest(qRes)
        else:
            tmpStr = str(status)
            tmpStr = tmpStr.replace("entities:", "")
            tmpStr = tmpStr.replace("topic:", "")
            tmpStr += "?"
            payload = tmpStr
        return payload

    def retrieveSelectedSources(self,qString, costType, cost):
        qRes, status = self._qEngine.processQuery(qString,10)
        self._costType = costType
        if status == "OK":
            if len(qRes) == 0:
                payload = "No results found!"
            else:
                # Find sources
                activeClusters = set([])
                for cid in qRes:
                    # get cluster
                    #cgraph.manager().clusters()[cid].printClusterSummary(cgraph._cEntRefToName,cgraph._cTopicToName)
                    activeClusters.add(self._cgraph.manager().clusters()[cid])
                pareto = ParetoFront.ParetoFront(['cov','time','bias'],activeClusters,cost,costType,self._cgraph.getSources())
                paretoPoints, dominatedPoints, solToProfile = pareto.findFront()
                self._selectionCache['paretoPoints'] = paretoPoints
                self._selectionCache['dominatedPoints'] = dominatedPoints
                self._selectionCache['solutionProfiles'] = solToProfile
                print solToProfile
                payload = "DONE"
                self._dataformater.selectionCSV(paretoPoints,dominatedPoints)
        else:
            tmpStr = str(status)
            tmpStr = tmpStr.replace("entities:", "")
            tmpStr = tmpStr.replace("topic:", "")
            tmpStr += "?"
            payload = tmpStr
        return payload

    def retrieveProfile(self,pointId):
        if not self._selectionCache['solutionProfiles']:
            payload = "No point profile found. Please issue query again."
        else:
            if pointId not in self._selectionCache['solutionProfiles']:
                payload = "No point profile found. Please issue query again."
            else:
                summary = []
                summary.append({'Metric':'Coverage', 'Value':str(round(100.0*self._selectionCache['solutionProfiles'][pointId]['cov'],2))+"%"})
                summary.append({'Metric':'Avg. Delay Lower 95% limit', 'Value':str(round(self._selectionCache['solutionProfiles'][pointId]['lowerD'],2))+" mins"})
                summary.append({'Metric':'Avg. Delay Upper 95% limit', 'Value':str(round(self._selectionCache['solutionProfiles'][pointId]['upperD'],2))+" mins"})
                summary.append({'Metric':'Polarity', 'Value':str(round(self._selectionCache['solutionProfiles'][pointId]['polarity'],2))})
                summary.append({'Metric':'Subjectivity', 'Value':str(round(self._selectionCache['solutionProfiles'][pointId]['subjectivity'],2))})
                summary.append({'Metric':'Cov. Gain', 'Value':str(round(self._selectionCache['solutionProfiles'][pointId]['covGain'],2))})
                summary.append({'Metric':'Delay Gain', 'Value':str(round(self._selectionCache['solutionProfiles'][pointId]['delayGain'],2))})
                summary.append({'Metric':'Bias Gain', 'Value':str(round(self._selectionCache['solutionProfiles'][pointId]['biasGain'],2))})
                if self._costType == "fixed":
                    summary.append({'Metric':'Sources Selected', 'Value':str(round(self._selectionCache['solutionProfiles'][pointId]['totalCost'],2))+" Sources"})
                else:
                    summary.append({'Metric':'Total Cost', 'Value':"$"+str(round(self._selectionCache['solutionProfiles'][pointId]['totalCost'],2))})
                    summary.append({'Metric':'Sources Selected', 'Value':str(len(self._selectionCache['solutionProfiles'][pointId]['selection']))+" Sources"})
                payload = json.dumps(summary)
        return payload

    def retrieveSourcesProfile(self,pointId):
        if not self._selectionCache['solutionProfiles']:
            payload = "No point profile found. Please issue query again."
        else:
            if pointId not in self._selectionCache['solutionProfiles']:
                payload = "No point profile found. Please issue query again."
            else:
                result = []
                metrics = ['cov','lowerD', 'upperD','polarity','subjectivity']
                sources = self._selectionCache['solutionProfiles'][pointId]['selection']
                for m in metrics:
                    newChart = {}
                    if m == 'cov':
                        newChart["chart_title"] = "Coverage"
                        newChart["unit"] = "percentage"
                        for s in sources:
                            sName = self._selectionCache['solutionProfiles'][pointId]['srcInfo'][s]['name']
                            sValue = self._selectionCache['solutionProfiles'][pointId]['srcInfo'][s]['cov']
                            newChart[sName] = sValue
                    elif m == 'lowerD':
                        newChart["chart_title"] = "Avg. Delay Lower 95% limit"
                        newChart["unit"] = "Minutes"
                        for s in sources:
                            sName = self._selectionCache['solutionProfiles'][pointId]['srcInfo'][s]['name']
                            sValue = self._selectionCache['solutionProfiles'][pointId]['srcInfo'][s]['lowerD']
                            newChart[sName] = sValue
                    elif m == 'upperD':
                        newChart["chart_title"] = "Avg. Delay Upper 95% limit"
                        newChart["unit"] = "Minutes"
                        for s in sources:
                            sName = self._selectionCache['solutionProfiles'][pointId]['srcInfo'][s]['name']
                            sValue = self._selectionCache['solutionProfiles'][pointId]['srcInfo'][s]['upperD']
                            newChart[sName] = sValue
                    elif m == 'polarity':
                        newChart["chart_title"] = "Polarity"
                        newChart["unit"] = ""
                        for s in sources:
                            sName = self._selectionCache['solutionProfiles'][pointId]['srcInfo'][s]['name']
                            sValue = self._selectionCache['solutionProfiles'][pointId]['srcInfo'][s]['polarity']
                            newChart[sName] = sValue
                    else:
                        newChart["chart_title"] = "Subjectivity"
                        newChart["unit"] = ""
                        for s in sources:
                            sName = self._selectionCache['solutionProfiles'][pointId]['srcInfo'][s]['name']
                            sValue = self._selectionCache['solutionProfiles'][pointId]['srcInfo'][s]['subjectivity']
                            newChart[sName] = sValue
                    result.append(newChart)

                payload = json.dumps(result)
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
    factory = CGraphFactory("ws://0.0.0.0:8080", debug,inputDir)
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
