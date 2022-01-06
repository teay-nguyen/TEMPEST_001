import numpy as np
import sys

class TranspositionTable:
    def __init__(self):
        self.Exact = 0
        self.LowerBound = 1
        self.UpperBound = 2
        self.lookupFailed = -sys.maxsize
        self.enabled = True
        self.sign = np.sign
        self.immediateMateScore = 100000
        self.size = 64

    def Index(self, state):
        return state.ZobristKey % self.size

    def ClearEntries(self, entries):
        entries.clear()

    def getStoredMove(self, state, entries):
        return entries[self.Index(state)].move

    def attemptLookup(self, state, entries, depth, plyFromRoot, alpha, beta) -> int:
        if (not self.enabled) or not self.Index(state) in entries:
            return self.lookupFailed

        entry = entries[self.Index(state)]

        if entry.key == state.ZobristKey:
            if entry.depth >= depth:
                if entry.nodeType == self.Exact:
                    return entry.value

                if entry.nodeType == self.UpperBound and entry.value <= alpha:
                    return alpha

                if entry.nodeType == self.LowerBound and entry.value >= beta:
                    return beta

        return self.lookupFailed

    def storeEval(self, state, entries, depth, plySearched, eval, evalType, move):
        if not self.enabled:
            return

        entry = Entry(state.ZobristKey, eval, depth, evalType, move)
        entries[self.Index(state)] = entry

    '''
    def CorrectScoreForStorage(self, score, plySearched) -> int:
        if (self.isMateScore(score)):
            sign = self.sign(score)
            return (score * sign + plySearched) * sign

        return score

    def CorrectRetrievedScore(self, score, plySearched) -> int:
        if (self.isMateScore(score)):
            sign = self.sign(score)
            return (score * sign - plySearched) * sign

        return score

    def isMateScore(self, score) -> bool:
        maxMateDepth = 1000
        return abs(score) > (self.immediateMateScore - maxMateDepth)
    '''


class Entry:
    def __init__(self, key, val, depth, nodeType, move):
        self.key = key
        self.value = val
        self.depth = depth
        self.nodeType = nodeType
        self.move = move
