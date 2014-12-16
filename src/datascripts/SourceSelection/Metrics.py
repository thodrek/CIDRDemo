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
    return coveredEntries/totalEntries


def timeliness(selection, activeClusters):
    return 1.0
