__author__ = 'thodoris'
import glob
import os
import sys
import cPickle as pickle

class DataLoader:

    def __init__(self,dataDir):
        self._files = []

        for file in os.listdir(dataDir):
            if file.endswith(".pkl"):
                self._files.append(dataDir+"/"+file)

        self._partitionedInput = {}


    def generateInput(self):
        # Load data
        loaded = 0
        total_files = len(self._files)
        for inputFile in self._files:
            print "Loading new files...",
            data = pickle.load(open(inputFile,"rb"))
            print "DONE."

            # Partition articles on topics
            events_processed = 0.0
            total_entries = len(data)
            print "Partitioning articles to topics...",
            for e in data:
                for ar in data[e]:
                    for t in ar['topics']:
                        tRef = t['namedRef']
                        tName = t['name']
                        if tRef not in self._partitionedInput:
                            self._partitionedInput[tRef] = {}
                            self._partitionedInput[tRef]['name'] = tName
                            self._partitionedInput[tRef]['articles'] = []
                        self._partitionedInput[tRef]['articles'].append(ar)
                # print progress
                events_processed += 1.0
                progress = events_processed*100.0/float(total_entries)
                sys.stdout.write("Event processing progress: %10.2f%% (%d out of %d, %d files read out of %d)   \r" % (progress,events_processed,total_entries, loaded, total_files))
                sys.stdout.flush()
            print "\n"
        loaded +=1

    def getInput(self):
        return self._partitionedInput


