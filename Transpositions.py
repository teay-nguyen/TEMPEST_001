import sys

class TranspositionTable:
    def __init__(self):
        self.Exact = 0
        self.LowerBound = 1
        self.UpperBound = 2
        self.size = 6400
        self.lookupFailed = -sys.maxsize
        self.enabled = True
        self.sign = lambda a: (a > 0) - (a < 0)
        self.immediateMateScore = 100000

    def ClearEntries(self, entries):
        entries.clear()

    def Index(self, state):
        return state.ZobristKey

    def getStoredMove(self, state, entries):
        return entries[self.Index(state)].move

    def attemptLookup(self, state, entries, depth, plyFromRoot, alpha, beta):
        if not self.enabled:
            return self.lookupFailed

        entry = entries[self.Index(state)]

        if entry.key == state.ZobristKey:
            if entry.depth >= depth:
                correctedScore = self.CorrectRetrievedScore(entry.value, plyFromRoot)

                if entry.nodeType == self.Exact:
                    return correctedScore

                if entry.nodeType == self.UpperBound and correctedScore <= alpha:
                    return correctedScore

                if entry.nodeType == self.LowerBound and correctedScore >= beta:
                    return correctedScore

    def storeEval(self, state, entries, depth, plySearched, eval, evalType, move):
        if not self.enabled:
            return

        entry = Entry(state.ZobristKey, self.CorrectScoreForStorage(eval, plySearched), depth, evalType, move)
        entries[self.Index(state)] = entry

    def CorrectScoreForStorage(self, score, plySearched):
        if self.isMateScore(score):
            sign = self.sign(score)
            return (score * sign + plySearched) * sign

        return score

    def CorrectRetrievedScore(self, score, plySearched):
        if self.isMateScore(score):
            sign = self.sign(score)
            return (score * sign - plySearched) * sign

        return score

    def isMateScore(self, score):
        maxMateDepth = 1000
        return abs(score) > (self.immediateMateScore - maxMateDepth)



class Entry:
    def __init__(self, key, val, depth, nodeType, move):
        self.key = key
        self.value = val
        self.depth = depth
        self.nodeType = nodeType
        self.move = move
