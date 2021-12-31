import sys


class TranspositionTable:
    def __init__(self, maxSize):
        self.Exact = 0
        self.LowerBound = 1
        self.UpperBound = 2
        self.entries = []
        self.Size = maxSize
        self.enabled = True

    def Clear(self):
        self.entries.clear()


class Entry:
    def __init__(self, key, value, move, depth, nodeType):
        self.key = key
        self.value = value
        self.move = move
        self.depth = depth
        self.nodeType = nodeType

    def getSize(self):
        return sys.getsizeof(self)
