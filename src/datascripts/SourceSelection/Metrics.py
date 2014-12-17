__author__ = 'thodoris'

from bitarray import bitarray

def computeCoveredEntries(selection,cluster):
    totalCont = None
    for srcId in selection:
        srcCont = cluster.getSrcContent(srcId)
        if srcCont:
            if totalCont:
                totalCont |= srcCont
            else:
                totalCont = srcCont

    if totalCont:
        return float(totalCont.count())
    else:
        return 0.0

def computeAggBias(selection, cluster):
    totalCont = 0.0
    polarity = 0.0
    subjectivity = 0.0
    for srcId in selection:
        srcBias = cluster.getSrcBias(srcId)
        if srcBias:
            totalCont += srcBias['total']
            polarity += srcBias['total']*srcBias['polarity']
            subjectivity += srcBias['total']*srcBias['subjectivity']
    if totalCont != 0.0:
        polarity = polarity/totalCont
        subjectivity = subjectivity/totalCont
    return polarity, subjectivity



def coverage(selection, activeClusters):

    if len(selection) == 0:
        return 0.0

    coveredEntries = 0.0
    totalEntries = 0.0

    for cluster in activeClusters:
        # compute covered items and total items
        coveredEntries += computeCoveredEntries(selection,cluster)
        totalEntries += cluster.getEvents()

    # compute final coverage
    if totalEntries == 0.0:
        return 0.0
    return coveredEntries/totalEntries

def bias(selection, activeClusters):
    if len(selection) == 0:
        return None, None

    polarity = 0.0
    subjectivity = 0.0
    totalEntries = 0.0
    for cluster in activeClusters:
        cEntries = computeCoveredEntries(selection, cluster)
        cPolarity, cSubjectivity = computeAggBias(selection, cluster)
        polarity += cEntries*cPolarity
        subjectivity += cEntries*cSubjectivity
        totalEntries += cEntries

    if totalEntries == 0.0:
        return None, None
    polarity = polarity/totalEntries
    subjectivity = subjectivity/totalEntries
    return polarity, subjectivity

def probCoveredEntryWithDelay(selection, cluster, delay):
    probProduct = 1.0
    for srcId in selection:
        probProduct *= 1.0 - cluster.getSrcDelayedCov(srcId,delay)
    finalProb = 1.0 - probProduct
    return finalProb

def probCovered(selection, cluster):
    probProduct = 1.0
    for srcId in selection:
        probProduct *= 1.0 - cluster.getSrcCoverage(srcId)
    finalProb = 1.0 - probProduct
    return finalProb

def timeliness(selection, activeClusters):
    if len(selection) == 0:
        return None, None

    # define delay intervals: immediately, 10mins, 1hour, 3hours, 6hours, 12hours, 18hours, 24hours, 2days, 3days, 4days, 5days, 7days, 10days]
    delayIntervals = [0.0, 10.0, 60.0, 180.0, 360.0, 720.0, 1080.0, 1440.0, 2880.0, 4320.0, 5760.0, 7200.0, 10080.0, 14400.0]

    # for each interval compute the probability of an event being captured with a delay up to that time
    probability = []
    for delay in delayIntervals:
        print "\nNew delay value",delay
        totalEntries = 0.0
        for cluster in activeClusters:
            totalEntries += cluster.getEvents()

        delayProb = 0.0
        for cluster in activeClusters:
            probCluster = cluster.getEvents()/totalEntries
            numProb = probCoveredEntryWithDelay(selection,cluster,delay)
            denomProb = probCovered(selection,cluster)
            if denomProb == 0.0:
                probCaptured = 0.0
            else:
                probCaptured = numProb/denomProb
            delayProb += probCaptured*probCluster

        probability.append(delayProb)

    return delayIntervals, probability
