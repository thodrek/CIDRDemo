__author__ = 'thodrek'


import cPickle as pickle
import argparse
import sys
from CorrespondenceGraph import CGraph
from SourceSelection import LocalSearch
from SourceSelection import GainFunction
from SourceSelection import CostFunction
from SourceSelection import Metrics


# Read input arguments
print "Reading input args...",
parser = argparse.ArgumentParser(description='Please use script as "python createCorrespondenceClusters.py -i <input_file>.')
parser.add_argument('-i','--input',help="Specifies input articles file.",required=True)
args = vars(parser.parse_args())
inputFile = args['input']
print "DONE."

# Load data
print "Loading data...",
data = pickle.load(open(inputFile,"rb"))
print "DONE."


# Partition articles on topics
events_processed = 0.0
total_entries = len(data)
partitionedInput = {}
print "Partitioning articles to topics...",
for e in data:
    for ar in data[e]:
        for t in ar['topics']:
            tRef = t['namedRef']
            tName = t['name']
            if tRef not in partitionedInput:
                partitionedInput[tRef] = {}
                partitionedInput[tRef]['name'] = tName
                partitionedInput[tRef]['articles'] = []
            partitionedInput[tRef]['articles'].append(ar)
    # print progress
    events_processed += 1.0
    progress = events_processed*100.0/float(total_entries)
    sys.stdout.write("Event processing progress: %10.2f%% (%d out of %d)   \r" % (progress,events_processed,total_entries))
    sys.stdout.flush()
print "\n"

# build correspondence graph
cgraph = CGraph.CGraph()
cgraph.generate(partitionedInput)
cgraph.summary()
print "Start building quality profiles..."
cgraph.manager().buildQualityProfiles()
print "\nDONE"

print "Start building pricing profiles..."
cgraph.manager().buildPricingProfiles()
print "\nDONE"

print "Build query engine"
qEngine = CGraph.QueryEngine("/tmp/index",cgraph)
qEngine.generateIndex()

print "\nIssue a test query and select sources"
qRes = qEngine.processQuery("entities:Obama")
activeClusters = set([])
for cid in qRes:
    # get cluster
    #cgraph.manager().clusters()[cid].printClusterSummary(cgraph._cEntRefToName,cgraph._cTopicToName)
    activeClusters.add(cgraph.manager().clusters()[cid])

gWeights = {"cov":0.1, "time":0.1, "bias":0.8}
gf = GainFunction.GainFunction(gWeights)
cf = CostFunction.CostFunction("fixed")
ls = LocalSearch.LocalSearch(activeClusters,gf,cf,10)
selection, gain, cost, util = ls.selectSources()

print "Gain = ",gain
print "Cost = ",cost
print "Util = ",util
print "Selected sources:"
for s in selection:
    print cgraph.getSourceName(s)

selection, gain, cost, util = ls.selectSourcesGreedy()

print "Gain = ",gain
print "Cost = ",cost
print "Util = ",util
print "Selected sources:"
for s in selection:
    print cgraph.getSourceName(s)

delayIntervals, probability = Metrics.timeliness(selection,activeClusters)
print delayIntervals
print probability

polarity, subjectivity = Metrics.bias(selection,activeClusters)
print polarity
print subjectivity





