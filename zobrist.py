import random


class Zobrist:
    def __init__(self):
        self.zobTable = [[[random.randint(
            1, 2**64 - 1) for i in range(12)]for j in range(8)]for k in range(8)]

    def index(piece):
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
