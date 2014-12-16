__author__ = 'thodoris'


class LocalSearch:

    def __init__(self, activeClusters, gainFunction, costFunction, maxCost):
        self._activeClusters = activeClusters
        self._epsilon = 0.001
        self._gainFunction = gainFunction
        self._costFunction = costFunction
        self._selectedSources = None
        self._selectionGain = -1.0
        self._selectionCost = -1.0
        self._selectionUtil = -1.0
        self._maxCost = maxCost

    def findAvailableSources(self):
        availableSrcIds = set([])
        for c in self._activeClusters:
            availableSrcIds |= set(c.sources())
        return availableSrcIds

    def selectSources(self):
        # initialize available sources
        availSources = self.findAvailableSources()

        # initialize selected sources
        tmpSelection = set([])

        # initialize gain, cost and utility metircs
        curGain = 0.0
        curCost = 0.0
        curUtil = float("-inf")
        srcToAdd = None

        # find best single source
        for srcId in availSources:
            tmpSelection.add(srcId)

            newGain = self._gainFunction.compute(tmpSelection,self._activeClusters)
            newCost = self._costFunction.compute(tmpSelection)
            newUtil = newGain - newCost

            if newUtil > curUtil and newCost <= self._maxCost:
                srcToAdd = srcId
                curUtil = newUtil
                curGain = newGain
                curCost = newCost

            tmpSelection.remove(srcId)

        # remove best source from available sources and add it to selected sources
        tmpSelection.add(srcToAdd)
        availSources.remove(srcToAdd)

        # Iterate until you find local optimum
        changed = True
        while changed:
            # init loop
            changed = False
            srcToAdd = None
            srcToRemove = None

            # add operation
            for srcId in availSources:
                # add source to selection and see if solution is improved
                tmpSelection.add(srcId)

                newGain = self._gainFunction.compute(tmpSelection,self._activeClusters)
                newCost = self._costFunction.compute(tmpSelection)
                newUtil = newGain - newCost

                if newUtil > curUtil and newCost <= self._maxCost:
                    srcToAdd = srcId
                    curUtil = newUtil
                    curGain = newGain
                    curCost = newCost
                    break

                # revert changes
                tmpSelection.remove(srcId)

            if srcToAdd:
                # commit changes
                availSources.remove(srcToAdd)
                changed = True
            else:
                # delete operation
                for srcId in tmpSelection:
                    # remove source from selection and see if solution is improved
                    tmpSelection.remove(srcId)

                    newGain = self._gainFunction.compute(tmpSelection, self._activeClusters)
                    newCost = self._costFunction.compute(tmpSelection)
                    newUtil = newGain - newCost

                    if newUtil > curUtil and newCost <= self._maxCost:
                        srcToRemove = srcId
                        curUtil = newUtil
                        curGain = newGain
                        curCost = newCost
                        break

                    # revert changes
                    tmpSelection.add(srcId)


                if srcToAdd:
                    # commit changes
                    availSources.add(srcToRemove)
                    changed = True

        # set selection result
        self._selectedSources = tmpSelection
        self._selectionGain = curGain
        self._selectionCost = curCost
        self._selectionUtil = curUtil
        return tmpSelection, curGain, curCost, curUtil


    def selectedSources(self):
        return self._selectedSources

