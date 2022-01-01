import sys

class TranspositionTable:
    def __init__(self, maxSize):
        self.Exact = 0
        self.LowerBound = 1
        self.UpperBound = 2
        self.lookUpFailed = -sys.maxsize - 1
        self.entries = {}
        self.Size = maxSize
        self.enabled = True

    def Clear(self):
        self.entries.clear()

    def Index(self, state):
        return state.ZobristKey % self.Size

    def StoreEvaluation(self, state, depth, numPlySearched, eval, evalType, move):
        if not self.enabled:
            return

        entry = Entry(state.ZobristKey, self.CorrectScoreForStorage(eval, numPlySearched), depth, evalType, move)
        self.entries[self.Index(state)] = entry

    def CorrectScoreForStorage(self, score, numPlySearched):
        pass

    def CorrectRetrievedScore(self, score, numPlySearched):
        pass


class Entry:
    def __init__(self, key, value, depth, nodeType, move):
        self.key = key
        self.value = value
        self.move = move
        self.depth = depth
        self.nodeType = nodeType

    def getSize(self):
        return sys.getsizeof(self)
