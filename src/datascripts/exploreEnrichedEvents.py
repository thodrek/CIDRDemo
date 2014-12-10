__author__ = 'thodrek'

import cPickle as pickle
import argparse
import datetime
import socket
import os
import sys

# Read input arguments
parser = argparse.ArgumentParser(description='Please use script as "python exploreEnrichedEvents.py -i <input_file>.')
parser.add_argument('-i','--input',help="Specifies input file.",required=True)
args = vars(parser.parse_args())

inputFile = args['input']

# Load input file
print "Loading input data...",
eventsInfo = pickle.load( open( inputFile, "rb" ) )
print "DONE."

# Extract topics for events
eKeys = eventsInfo.keys()
for eKey in eKeys[:4]:
    topics = {}
    entities = {}
    totalConf = 0.0
    for ar in eventsInfo[eKey]:
        print "Event article title = ",ar['title']
        for e in ar['entities']:
            if e['name'] not in entities:
                entities[e['name']] = 0.0
            entities[e['name']] += 1.0
        for t in ar['topics']:
            if t['name'] not in topics:
                topics[t['name']] = 0.0
            topics[t['name']] += t['score']
            totalConf += t['score']
    print "Event topics = "
    for t in topics:
        print t, topics[t]/totalConf
    print "Event entities = "
    for e in entities:
        print e, entities[e]
