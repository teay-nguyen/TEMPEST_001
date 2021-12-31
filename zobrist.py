import random


class Zobrist:
    def __init__(self):
        self.seed = 592735
        self.zobTable = [[[random.randint(
            1, 2**64 - 1) for i in range(12)]for j in range(8)]for k in range(8)]

    def index(self, piece):
        if (piece == 'wp'):
            return 0
        if (piece == 'wN'):
            return 1
        if (piece == 'wB'):
            return 2
        if (piece == 'wR'):
            return 3
        if (piece == 'wQ'):
            return 4
        if (piece == 'wK'):
            return 5
        if (piece == 'bp'):
            return 6
        if (piece == 'bN'):
            return 7
        if (piece == 'bB'):
            return 8
        if (piece == 'bR'):
            return 9
        if (piece == 'bQ'):
            return 10
        if (piece == 'bK'):
            return 11
        else:
            return -1

    def CalculateZobristKey(self, state):
        board = state.board
        zobristKey = 0

        for row in range(8):
            for col in range(8):
                if board[row][col] != '--':
                    piece = self.index(board[row][col])
                    zobristKey ^= self.zobTable[row][col][piece]

        epPossible = state.epPossible
        if epPossible != ():
            zobristKey ^= (epPossible[0] + epPossible[1])

        sideToMove = 1 if state.whitesturn else -1
        zobristKey ^= sideToMove

        castleRights = state.currCastleRights

    def checkCastleRights(self, castleRights):
        wks = castleRights.wks
        wqs = castleRights.wqs
        bks = castleRights.bks
        bqs = castleRights.bqs

        pass
