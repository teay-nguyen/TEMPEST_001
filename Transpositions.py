import sys

class TranspositionTable:
    def __init__(self, maxSize):
        self.Exact = 0
        self.LowerBound = 1
        self.UpperBound = 2
        self.lookUpFailed = -sys.maxsize - 1
        self.entries = {}
        self.size = maxSize
        self.enabled = True
        self.sign = lambda a: (a > 0) - (a < 0)

    def Clear(self):
        self.entries.clear()

    def Index(self, state):
        return state.ZobristKey % self.size

    def getStoredMove(self, state):
        return self.entries[self.Index(state)].move

    def attemptEvalLookup(self, s, state, depth, plyFromRoot, alpha, beta):
        if not self.enabled:
            return self.lookUpFailed

        entry = self.entries[self.Index(state)]

        if (entry.key == state.ZobristKey):
            if (entry.depth >= depth):
                correctedScore = self.CorrectedRetrievedMateScore(s, entry.value, plyFromRoot)

                if (entry.nodetype == self.Exact):
                    return correctedScore

                if (entry.nodetype == self.UpperBound) and (correctedScore <= alpha):
                    return correctedScore

                if (entry.nodetype == self.LowerBound) and (correctedScore >= beta):
                    return correctedScore

        return self.lookUpFailed

    def storeEval(self, s, state, depth, numPlySearched, eval, evalType, move):
        if not self.enabled:
            return

        if len(self.entries.keys()) > self.size:
            entry = Entry(state.ZobristKey, self.CorrectedMateScore(s, eval, numPlySearched), depth, evalType, move)
            self.entries[self.Index(state)] = entry
        else:
            print('TranspositionTable full, try again when there is space!')
            return

    def CorrectedMateScore(self, s, score, numPlySearched):
        if (s.IsMateScore(score)):
            sign = self.sign(score)
            return (score * sign + numPlySearched) * sign

        return score

    def CorrectedRetrievedMateScore(self, s, score, numPlySearched):
        if (s.IsMateScore(score)):
            sign = self.sign(score)
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
