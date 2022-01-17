import random

zobTable = [[[random.randint(1, 2**64 - 1) for i in range(12)]
             for j in range(8)]for k in range(8)]
randomSeed = random.randrange(10000, 99999)
multiply_seed = [16, 20, 24, 28]

class Zobrist:
    def __init__(self):
        self.seed = randomSeed
        self.zobTable = zobTable

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

        zobristKey ^= self.checkCastleRights(state.currCastleRights)
        zobristKey ^= self.seed

        return zobristKey

    def checkCastleRights(self, castleRights):
        castle_key = 17

        wks = castleRights.wks
        wqs = castleRights.wqs
        bks = castleRights.bks
        bqs = castleRights.bqs

        if wks == True:
            castle_key *= multiply_seed[0]
        if wqs == True:
            castle_key *= multiply_seed[1]
        if bks == True:
            castle_key *= multiply_seed[2]
        if bqs == True:
            castle_key *= multiply_seed[3]

        return castle_key
