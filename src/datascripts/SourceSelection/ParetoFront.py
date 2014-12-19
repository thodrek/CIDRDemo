__author__ = 'thodrek'
import itertools
import sys
from SourceSelection import LocalSearch
from SourceSelection import GainFunction
from SourceSelection import CostFunction
from SourceSelection import Metrics
class ParetoFront:

    def __init__(self,qualMetrics, activeClustes, cost, costType):
        self._qualMetrics = qualMetrics
        self._activeClusters = activeClustes
        self._cost = cost
        self._costType = costType

    def _dominates(self, row, candidateRow):
        rowData = row[1]
        candidateRowData = candidateRow[1]
        return sum([rowData[x] >= candidateRowData[x] for x in range(len(rowData))]) == len(rowData)

    def _simple_cull(self, inputPoints):
        paretoPoints ={}
        candidateRowNr = 0
        dominatedPoints = {}
        while True:
            candidateRow = inputPoints[candidateRowNr]
            inputPoints.remove(candidateRow)
            rowNr = 0
            nonDominated = True
            while len(inputPoints) != 0 and rowNr < len(inputPoints):
                row = inputPoints[rowNr]
                if self._dominates(candidateRow, row):
                    # If it is worse on all features remove the row from the array
                    inputPoints.remove(row)
                    dominatedPoints[row[0]] = row[1]
                elif self._dominates(row, candidateRow):
                    nonDominated = False
                    dominatedPoints[candidateRow[0]] = candidateRow[1]
                    rowNr += 1
                else:
                    rowNr += 1

            if nonDominated:
                # add the non-dominated point to the Pareto frontier
                paretoPoints[candidateRow[0]] = candidateRow[1]

            if len(inputPoints) == 0:
                break
        return paretoPoints, dominatedPoints

    def findFront(self):
        # build weight grid if there are multiple metrics
        weightCombs = []
        activeMetrics = float(len(self._qualMetrics))
        gridValues = range(0,110,10)
        gridValues = [float(x)/100.0 for x in gridValues]

        if activeMetrics == 1.0:
            newComb = {"cov":0.0, "time":0.0, "bias":0.0}
            newComb[self._qualMetrics[0]] = 1.0
            weightCombs.append(newComb)
        elif activeMetrics == 2.0:
            allCombos = list(itertools.product(gridValues,gridValues))
            validCombos = []
            for c in allCombos:
                if sum(c) == 1.0:
                    validCombos.append(c)
            for c in validCombos:
                newComb = {"cov":0.0, "time":0.0, "bias":0.0}
                newComb[self._qualMetrics[0]] = c[0]
                newComb[self._qualMetrics[1]] = c[1]
                weightCombs.append(newComb)
        else:
            allCombos = list(itertools.product(gridValues, gridValues))
            allCombos = list(itertools.product(gridValues, allCombos))
            validCombos = []
            for c in allCombos:
                if c[0] + sum(c[1]) == 1.0:
                    validCombos.append((c[0],c[1][0],c[1][1]))
            for c in validCombos:
                newComb = {"cov":0.0, "time":0.0, "bias":0.0}
                newComb[self._qualMetrics[0]] = c[0]
                newComb[self._qualMetrics[1]] = c[1]
                newComb[self._qualMetrics[2]] = c[2]
                weightCombs.append(newComb)
            newComb = {"cov":0.34, "time":0.33, "bias":0.33}
            weightCombs.append(newComb)


        # for each sample point find best solution
        entries_processed = 0.0
        total_entries = len(weightCombs)

        solValues = []
        solToProfile = {}
        solIndex = 0
        for combo in weightCombs:
            gWeights = combo
            gf = GainFunction.GainFunction(gWeights)
            cf = CostFunction.CostFunction(self._costType)
            ls = LocalSearch.LocalSearch(self._activeClusters,gf,cf, self._cost)
            selection, gain, cost, util = ls.selectSources()
            profile = ls.selectionProfile()
            # store solution profile
            profile['totalGain'] = gain
            profile['totalCost'] = cost
            profile['selection'] = selection
            solToProfile[solIndex] = profile
            # store values
            solValues.append((solIndex,[profile['covGain'], profile['delayGain'], profile['biasGain']]))
            solIndex += 1

            # update progress bar
            entries_processed += 1.0
            progress = entries_processed*100.0/total_entries
            sys.stdout.write("Approximating pareto front... Progress: %10.2f%% (%d out of %d)   \r" % (progress,entries_processed,total_entries))
            sys.stdout.flush()

        # find pareto optimal points
        paretoPoints, dominatedPoints = self._simple_cull(solValues)

        return paretoPoints, dominatedPoints, solToProfile
