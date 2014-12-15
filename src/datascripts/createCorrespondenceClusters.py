__author__ = 'thodrek'


import cPickle as pickle
import argparse
import sys
from CorrespondenceGraph import CGraph


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

print "Build query engine"
qEngine = CGraph.QueryEngine("/tmp/index",cgraph)
qEngine.generateIndex()

print "\n Issue a test query"
qRes = qEngine.processQuery("entities:Obama")
for cid in qRes:
    # get cluster
    c = cgraph.manager().clusters()[cid].printCovSummary()
