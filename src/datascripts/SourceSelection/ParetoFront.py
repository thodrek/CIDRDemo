__author__ = 'thodrek'

class ParetoFront:

    def __init__(self,qualMetrics):
        self._qualMetrics = qualMetrics

    def _dominates(self, row, candidateRow):
        return sum([row[x] >= candidateRow[x] for x in range(len(row))]) == len(row)

    def _simple_cull(self, inputPoints):
        paretoPoints = set()
        candidateRowNr = 0
        dominatedPoints = set()
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
                    dominatedPoints.add(tuple(row))
                elif self._dominates(row, candidateRow):
                    nonDominated = False
                    dominatedPoints.add(tuple(candidateRow))
                    rowNr += 1
                else:
                    rowNr += 1

            if nonDominated:
                # add the non-dominated point to the Pareto frontier
                paretoPoints.add(tuple(candidateRow))

            if len(inputPoints) == 0:
                break
        return paretoPoints, dominatedPoints

    def findFront(self):
        # initialize weight combinations add basic configuration
        weightCombs = []
        activeMetrics = float(len(self._qualMetrics))
        newComb = {"cov":0.0, "time":0.0, "bias":0.0}
        for metric in self._qualMetrics:
            newComb[metric] = 1.0/activeMetrics
        weightCombs.append(newComb)

        # build weight grid if there are multiple metrics
        if activeMetrics > 1.0:



        if 'cov' in self._qualMetrics:
            covWeights

        # for each sample point find best solution

        # find pareto optimal points

        gWeights = {"cov":0.1, "time":0.1, "bias":0.8}
        gf = GainFunction.GainFunction(gWeights)
        cf = CostFunction.CostFunction("fixed")
        ls = LocalSearch.LocalSearch(activeClusters,gf,cf,10)
        selection, gain, cost, util = ls.selectSources()
        return None
