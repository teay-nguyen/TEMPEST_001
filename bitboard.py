
import numpy as np


class Bitboard:
    def __init__(self, state):
        self.state = state
        self.bitboard = np.zeros((8, 8))

    def attacked_squares(self):
        self.state.whitesturn = not self.state.whitesturn
        oppMoves = self.state.FilterValidMoves()
        self.state.whitseturn = not self.state.whitesturn

        attackSquares = []
        oppPawnAttackMap = self.state.oppPawnAttackMap['Black' if self.state.whitesturn else 'White']
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

        print(self.bitboard)


if __name__ == '__main__':
    from engine import State

    e = State()
    b = Bitboard(e)

    b.attacked_squares()
