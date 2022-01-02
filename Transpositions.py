import sys
from DepthLiteThink import DepthLite1

DepthLite = DepthLite1()

class TranspositionTable:
    def __init__(self, maxSize):
        self.Exact = 0
        self.LowerBound = 1
        self.UpperBound = 2
        self.lookUpFailed = -sys.maxsize

        self.entries = {}
        self.size = maxSize
        self.enabled = True
        self.sign = lambda a: (a > 0) - (a < 0)

    def Clear(self):
        self.entries.clear()

    def getStoredMove(self, state):
        return self.entries[state.ZobristKey % self.size].move

    def attemptLookup(self, state, depth, plyFromRoot, alpha, beta):
        if not self.enabled:
            return self.lookUpFailed

        entry = self.entries[state.ZobristKey % self.size]
        if entry.key == state.ZobristKey:
            if entry.depth >= depth:
                correctedScore = self.CorrectRetrievedMateScore(entry.value, plyFromRoot)

                if entry.nodeType == self.Exact:
                    return correctedScore

                if entry.nodeType == self.UpperBound and correctedScore <= alpha:
                    return correctedScore
                
                if entry.nodeType == self.LowerBound and correctedScore >= beta:
                    return correctedScore


        return self.lookUpFailed

    def StoreEval(self, state, depth, plySearched, eval, evalType, move):
        if not self.enabled:
            return

        entry = Entry(state.ZobristKey, self.CorrectMateScoreForStorage(eval, plySearched), depth, evalType, move)
        self.entries[state.ZobristKey % self.size] = entry

    def CorrectMateScoreForStorage(self, score, plySearched):
        if (DepthLite.isMateScore(score)):
            sign = self.sign(score)
            return (score * sign + plySearched) * sign

        return score

    def CorrectRetrievedMateScore(self, score, plySearched):
        if (DepthLite.isMateScore(score)):
            sign = self.sign(score)
            return (score * sign - plySearched) * sign

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
