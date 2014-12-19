__author__ = 'thodoris'

import Metrics
from Utilities import functions

class LocalSearch:

    def __init__(self, activeClusters, gainFunction, costFunction, maxCost):
        self._activeClusters = activeClusters
        self._srcNames = {}
        self._epsilon = 0.001
        self._gainFunction = gainFunction
        self._costFunction = costFunction
        self._selectedSources = None
        self._selectionGain = -1.0
        self._selectionCost = -1.0
        self._selectionUtil = -1.0
        self._maxCost = maxCost
        self._selectionProfile = None

    def findAvailableSources(self):
        availableSrcIds = set([])
        for c in self._activeClusters:
            cSrcs = c.sources()
            availableSrcIds |= set(cSrcs)
            for sid in cSrcs:
                self._srcNames[sid] = c.getSrcName(sid)
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

                # revert changes
                tmpSelection.remove(srcId)

            if srcToAdd:
                # commit changes
                tmpSelection.add(srcToAdd)
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

                    # revert changes
                    tmpSelection.add(srcId)


                if srcToRemove:
                    # commit changes
                    availSources.add(srcToRemove)
                    tmpSelection.remove(srcToRemove)
                    changed = True

        # set selection result
        self._selectedSources = tmpSelection
        self._selectionGain = curGain
        self._selectionCost = curCost
        self._selectionUtil = curUtil
        return tmpSelection, curGain, curCost, curUtil


    def selectSourcesGreedy(self):
        # initialize available sources
        availSources = self.findAvailableSources()

        # initialize selected sources
        tmpSelection = set([])

        # initialize gain, cost and utility metircs
        curGain = 0.0
        curCost = 0.0
        curUtil = float("-inf")
        srcToAdd = None

        # Iterate until you find local optimum
        changed = True
        while changed:
            # init loop
            changed = False
            srcToAdd = None

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

                # revert changes
                tmpSelection.remove(srcId)

            if srcToAdd:
                # commit changes
                tmpSelection.add(srcToAdd)
                availSources.remove(srcToAdd)
                changed = True

        return tmpSelection, curGain, curCost, curUtil

    def selectionProfile(self):
        if not self._selectedSources:
            return None
        else:
            # initialize profile
            profile = {}

            # compute coverage, delay bounds and bias
            cov = Metrics.coverage(self._selectedSources,self._activeClusters)
            upperD, lowerD = Metrics.delayBounds(self._selectedSources, self._activeClusters)
            polarity, subjectivity = Metrics.bias(self._selectedSources, self._activeClusters)

            profile['cov'] = cov
            profile['upperD'] = upperD
            profile['lowerD'] = lowerD
            profile['polarity'] = polarity
            profile['subjectivity'] = subjectivity
            profile['covGain'] = functions.covGain(cov)
            profile['delayGain'] = functions.timeGain(upperD,lowerD)
            profile['biasGain'] = functions.biasGain(polarity,subjectivity)

            # build source specific profiles
            profile['srcInfo'] = {}
            for s in self._selectedSources:
                srcProfile = {}

                # build src profile
                srcProfile['name'] = self._srcNames[s]
                sSel = set([s])
                sCov = Metrics.coverage(sSel, self._activeClusters)
                sUpperD, sLowerD = Metrics.delayBounds(sSel, self._activeClusters)
                sPolarity, sSubjectivity = Metrics.bias(sSel, self._activeClusters)

                srcProfile['cov'] = sCov
                srcProfile['upperD'] = sUpperD
                srcProfile['lowerD'] = sLowerD
                srcProfile['polarity'] = sPolarity
                srcProfile['subjectivity'] = sSubjectivity


                # store src profile
                profile['srcInfo'][s] = srcProfile

        self._selectionprofile = profile
        return profile

    def selectedSources(self):
        return self._selectedSources

