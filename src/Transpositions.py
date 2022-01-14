import numpy as np

class TranspositionTable:
    def __init__(self):
        self.Exact = 0
        self.BetaBound = 1
        self.AlphaBound = 2
        self.value = 0
        self.entries_size = 640000

    def init_entries(self):
        entries = [Entry(None, None) for _ in range(self.entries_size)]
        return entries

    def Index(self, state):
        return np.int64(np.mod(state.ZobristKey, self.entries_size))

    def ClearEntries(self, entries):
        if isinstance(entries, list):
            entries = [Entry(None, None) for _ in range(self.entries_size)]

    def getStoredMove(self, state, entries, key):
        if entries[self.Index(state)].key == None: return 0
        entry = entries[self.Index(state)]
        if entry.key == key: return entry.move
        return None

    def getStoredEval(self, state, entries, depth, alpha, beta) -> int:
        if entries[self.Index(state)].key == None: return 0
        entry = entries[self.Index(state)]
        if entry.key == state.ZobristKey and entry.depth >= depth:
            if (entry.nodeType == self.Exact):
                self.value = entry.value
                return 1
            if (entry.nodeType == self.AlphaBound) and (entry.value <= alpha):
                self.value = alpha
                return 1
            if (entry.nodeType == self.BetaBound) and (entry.value >= beta):
                self.value = beta
                return 1
        return 0

    def getStoredScore(self, state, entries):
        if self.Index(state) > self.entries_size: return
        entry = entries[self.Index(state)]
        if (entry.key == state.ZobristKey): return entry.value
        return None

    def storeEval(self, state, entries, depth, eval, evalType):
        if self.Index(state) > self.entries_size: return
        entry = entries[self.Index(state)]
        if (entry.depth > depth) and (entry.key == state.ZobristKey): return
        assert (isinstance(eval, int))
        assert (isinstance(depth, int))
        assert (isinstance(state.ZobristKey, int))
        entry.key = state.ZobristKey
        entry.value = eval
        entry.depth = depth
        entry.nodeType = evalType

    def storeMove(self, state, entries, depth, move):
        if self.Index(state) > self.entries_size: return
        entry = entries[self.Index(state)]
        if (entry.depth > depth) and (entry.key == state.ZobristKey): return
        assert (isinstance(depth, int))
        assert (isinstance(state.ZobristKey, int))
        entry.key = state.ZobristKey
        entry.depth = depth
        entry.move = move

    def storeScore(self, state, entries, score):
        if self.Index(state) > self.entries_size: return
        entry = entries[self.Index(state)]
        assert (isinstance(state.ZobristKey, int))
        assert (isinstance(score, int))
        entry.value = score
        entry.key = state.ZobristKey

class Entry:
    def __init__(self, key, val):
        self.key = key
        self.value = val
        self.depth = 0
        self.nodeType = 0
        self.move = None
