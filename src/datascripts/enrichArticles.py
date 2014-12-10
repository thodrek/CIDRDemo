__author__ = 'thodrek'

import cPickle as pickle
import argparse
import datetime
from calais import Calais
import socket
import os
import sys
import re

# init calais
API_KEYS = ['k8qqyqpzgck5k3hgmsfjrphf','n6p8psyvs2yqe4gzrttck5rv', '2ap3f4ycgn3bs3wjxsbkjsrk']
#API_KEY = '3x9q2sc5qtvqkqgdwmremkar'
calais_reqs = 0.0
calais_index = 0
calais = Calais(API_KEYS[calais_index],submitter="thodrek")

# Read input arguments
parser = argparse.ArgumentParser(description='Please use script as "python enrichArticles.py -a <input_art_file> -e <input_event_file>.')
parser.add_argument('-a','--articleInput',help="Specifies input articles file.",required=True)
parser.add_argument('-e','--eventInput',help="Specifies input events file.",required=True)
args = vars(parser.parse_args())

print "Reading input parameters...",
inputArFile = args['articleInput']
inputEvFile = args['eventInput']
# extract dates
inputTokens = inputArFile.rstrip('.pkl').split('_')
if socket.gethostname() == 'balos.umiacs.umd.edu':
    out_prefix = '/scratch0/CIDRDemo/EventReg_Data/articlesEnriched_'+inputTokens[2]+'_'+inputTokens[3]
else:
    out_prefix = '/tmp/articlesEnriched_'+inputTokens[2]+'_'+inputTokens[3]
print "DONE."

print "Loading input data...",
articleInfo = pickle.load( open( inputArFile, "rb" ) )
eventsInfo = pickle.load( open( inputEvFile, "rb" ) )
print "DONE."

# Iterate over events and enrich articles
print "Processing events and enriching articles..."
events_processed = 0.0
errors = 0.0
total_entries = len(articleInfo)
articlesEnriched = {}
for eKey in articleInfo:
    articlesEnriched[eKey] = []
    articles = articleInfo[eKey]
    # find min event date
    artMinDate = datetime.datetime.today()
    evDatetime = datetime.datetime.strptime(eventsInfo[eKey]['eventDate'], "%Y-%m-%d")
    for ar in articles:
        arDate = datetime.datetime.strptime(ar['date']+" "+ar['time'], "%Y-%m-%d %H:%M:%S")
        if arDate < artMinDate:
            artMinDate = arDate
    if evDatetime.date() >= artMinDate.date():
        evDatetime = artMinDate

    # enrich articles
    for ar in articles:
        newArticle = {}
        # add existing information
        newArticle['body'] = ar['body']
        newArticle['sourceTitle'] = ar['sourceTitle']
        newArticle['sourceUri'] = ar['sourceUri']
        newArticle['title'] = ar['title']
        newArticle['eventUri'] = ar['eventUri']
        newArticle['sourceId'] = ar['sourceId']
        newArticle['time'] = ar['time']
        newArticle['date'] = ar['date']
        newArticle['datetime'] = datetime.datetime.strptime(ar['date']+" "+ar['time'], "%Y-%m-%d %H:%M:%S")
        newArticle['id'] = ar['id']
        newArticle['uri'] = ar['uri']

        # compute delay in mention
        delay = newArticle['datetime'] - evDatetime
        delayMins = delay.total_seconds()/60.0
        newArticle['delay'] = delayMins
        newArticle['topics'] = []
        newArticle['entities'] = []

        # extract entities and topics from article
        calaisInput = ar['title'] + ' ' + ar['body']
        calaisInput = re.sub(r'[^\x00-\x7F]+',' ', calaisInput)
        try:
            calaisResult = calais.analyze(calaisInput)
            # store entities
            if hasattr(calaisResult, 'entities'):
                # calais entity schema ['_typeReference', '_type', 'name', '__reference', 'instances', 'relevance', 'nationality', 'organizationtype']
                for entity in calaisResult.entities:
                    newEntity = {}
                    newEntity['name'] = entity['name']
                    newEntity['type'] = entity['_type']
                    newEntity['cRef'] = entity['__reference']
                    newEntity['typeRef'] = entity['_typeReference']
                    newEntity['relevance'] = entity['relevance']

                    # add new entity to article entities
                    newArticle['entities'].append(newEntity)
            # store topics
            if hasattr(calaisResult, 'topics'):
                # calais topic schema ['category', 'categoryName', '__reference', 'classifierName', 'score']
                for topic in calaisResult.topics:
                    newTopic = {}
                    newTopic['name'] = topic['categoryName']
                    newTopic['namedRef'] = topic['category']
                    newTopic['idRef'] = topic['__reference']
                    newTopic['score'] = topic['score']

                    # add new topic to article topics
                    newArticle['topics'].append(newTopic)
            # add new article to event
            if len(newArticle['entities']) == 0 and len(newArticle['topics']) == 0:
                errors += 1.0
            else:
                articlesEnriched[eKey].append(newArticle)
        except Exception, err:
            print err
            errors += 1.0
        calais_reqs += 1
        if calais_reqs == 50000:
            calais_reqs = 0
            calais_index += 1
            calais = Calais(API_KEYS[calais_index],submitter="thodrek")
    # print progress
    events_processed += 1.0
    progress = events_processed*100.0/float(total_entries)
    sys.stdout.write("Event processing progress: %10.2f%% (%d out of %d, errors %d)   \r" % (progress,events_processed,total_entries, errors))
    sys.stdout.flush()

print "DONE."

print "Storing output to pickle dictionaries...",
out_filename = out_prefix+".pkl"
pickle.dump(articlesEnriched,open(out_filename,"wb"))
print "DONE."

# if on remote server transfer code to balos
if socket.gethostname() != 'balos.umiacs.umd.edu':
    os_command = "scp "+out_filename+" thodrek@balos.umiacs.umd.edu:/scratch0/CIDRDemo/EventReg_Data"
    x = os.system(os_command)
