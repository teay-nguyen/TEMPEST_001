
import numpy as np


class Bitboard:
    def __init__(self):
        self.bitboard = np.zeros((8, 8)) 

    def attacked_squares(self, state):
        state.whitesturn = not state.whitesturn
        oppMoves = state.getAllPossibleMoves()
        state.whitseturn = not state.whitesturn

        attackSquares = []
        index = 'Black' if state.whitesturn else 'White'
        oppPawnAttackMap = state.oppPawnAttackMap[index]

        for move in oppMoves:
            attacksq = (move.endRow, move.endCol)
            if move.pieceMoved[1] != 'p':
                self.bitboard[move.endRow, move.endCol] = 1
                attackSquares.append(attacksq)

            elif move.pieceMoved[1] == 'p':
                if attacksq in oppPawnAttackMap:
                    self.bitboard[move.endRow, move.endCol] = 1
                    attackSquares.append(attacksq)
