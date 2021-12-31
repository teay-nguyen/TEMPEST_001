import sys
from DepthLiteThink import StaticMethods
import numpy as np

class TranspositionTable:
    def __init__(self, maxSize):
        self.Exact = 0
        self.LowerBound = 1
        self.UpperBound = 2
        self.lookUpFailed = -2147483648
        self.entries = []
        self.Size = maxSize
        self.enabled = True
        self.StaticMethods = StaticMethods()

    def Clear(self):
        self.entries.clear()

    def StoreEvaluation(self, state, depth, numPlySearched, eval, evalType, move):
        if not self.enabled:
            return

        entry = Entry(state.ZobristKey, self.CorrectScoreForStorage(eval, numPlySearched), depth, evalType, move)
        self.entries.append(entry)

    def CorrectScoreForStorage(self, score, numPlySearched):
        if self.StaticMethods.isMateScore(score):
            signfunc = lambda x: (x > 0) - (x < 0)
            sign = signfunc(score)
            return (score * sign + numPlySearched) * sign
        return score

    def CorrectRetrievedScore(self, score, numPlySearched):
        if self.StaticMethods.isMateScore(score):
            signfunc = lambda x: (x > 0) - (x < 0)
            sign = signfunc(score)
            return (score * sign - numPlySearched) * sign
        return score

class Entry:
    def __init__(self, key, value, depth, nodeType, move):
        self.key = key
        self.value = value
        self.move = move
        self.depth = depth
        self.nodeType = nodeType

    def getSize(self):
        return sys.getsizeof(self)
