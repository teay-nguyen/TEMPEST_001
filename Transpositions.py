
class TranspositionTable:
    def __init__(self):
        self.Exact = 0
        self.LowerBound = 1
        self.UpperBound = 2
        self.NoneBound = 3
        self.value = 0

    def Index(self, state):
        return state.ZobristKey

    def ClearEntries(self, entries):
        entries.clear()

    def getStoredMove(self, state, entries, key):
        if not self.Index(state) in entries:
            return 0

        entry = entries[self.Index(state)]

        if entry.key == key:
            return entry.move

        return None

    def attemptLookup(self, state, entries, depth, alpha, beta) -> int:
        if not self.Index(state) in entries:
            return 0

        self.value = 0
        entry = entries[self.Index(state)]

        if entry.key == state.ZobristKey and entry.depth >= depth:
            if (entry.nodeType == self.Exact) | \
                    (entry.nodeType == self.UpperBound and entry.value <= alpha) | \
                    (entry.nodeType == self.LowerBound and entry.value >= beta):
                        self.value = entry.value
                        return 1
        return 0

    def storeEval(self, state, entries, depth, eval, evalType):
        entry = Entry(state.ZobristKey, eval)

        if entry.depth <= depth:
            entry.key = state.ZobristKey
            entry.value = eval
            entry.depth = depth
            entry.nodeType = evalType

            entries[self.Index(state)] = entry

    def storeMove(self, state, entries, depth, move):
        entry = Entry(state.ZobristKey, eval)

        if entry.depth <= depth:
            entry.key = state.ZobristKey
            entry.depth = depth
            entry.nodeType = self.NoneBound
            entry.move = move

            entries[self.Index(state)] = entry

class Entry:
    def __init__(self, key, val):
        self.key = key
        self.value = val
        self.depth = 0
        self.nodeType = 0
        self.move = None
