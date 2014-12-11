__author__ = 'thodrek'


import cPickle as pickle
import argparse
import sys
from fp_growth import find_frequent_itemsets


# frequent itemset approach for entities

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
articlesToTopics = {}
topicset = set([])
print "Partitioning articles to topics...",
for e in data:
    for ar in data[e]:
        for t in ar['topics']:
            tok = t['name'].split('_')
            if 'Finance' in tok:
                topicset.add(t['name'])
    # print progress
    events_processed += 1.0
    progress = events_processed*100.0/float(total_entries)
    sys.stdout.write("Event processing progress: %10.2f%% (%d out of %d)   \r" % (progress,events_processed,total_entries))
    sys.stdout.flush()
print "\n"
print "DONE."

print topicset


#itemsets = find_frequent_itemsets(transactions, 5, include_support=True)
