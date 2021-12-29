
class BoardRepresentation:
    def __init__(self):
        pass

    def RankIndex(self, squareIndex):
        return squareIndex >> 3

    def FileIndex(self, squareIndex):
        return squareIndex & 0b000111

    def IndexFromCoord(self, fileIndex, rankIndex):
        return rankIndex * 8 + fileIndex