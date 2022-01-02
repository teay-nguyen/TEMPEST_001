
import numpy as np


class Bitboard:
    def __init__(self):
        self.bitboard = np.zeros((8, 8))
        self.knightAttackBitboards = np.zeros((8, 8))
        self.kingAttackBitboards = np.zeros((8, 8))
        self.pawnAttackBitboards = np.zeros((8, 8))

    def attacked_squares(self, state):
        state.whitesturn = not state.whitesturn
        oppMoves = state.getAllPossibleMoves()
        state.whitseturn = not state.whitesturn

        attackSquares = []
        oppPawnAttackMap = state.oppPawnAttackMap['Black' if state.whitesturn else 'White']
        print(oppPawnAttackMap)

        for move in oppMoves:
            attacksq = (move.endRow, move.endCol)
            if move.pieceMoved[1] != 'p':
                self.bitboard[move.endRow, move.endCol] = 1.
                attackSquares.append(attacksq)

            elif move.pieceMoved[1] == 'p':
                if attacksq in oppPawnAttackMap:
                    self.bitboard[move.endRow, move.endCol] = 1.
                    attackSquares.append(attacksq)
