from Transpositions import TranspositionTable
from psqt import setBasicValues

class MoveOrdering:
    def __init__(self):
        self.moveScores = []
        self.tt = TranspositionTable()
        self.basic_values = setBasicValues()

    def score_move(self, move, hash_move):
        score = 0
        movePieceType = move.pieceMoved
        movePieceCaptured = move.pieceCaptured

        if movePieceCaptured != '--': score = (self.basic_values.piece_value[movePieceCaptured[1]] - self.basic_values.piece_value[movePieceType[1]])
        if move == hash_move: score += 10000

        return score

    def OrderMoves(self, state, moves, entries):
        hashMove = self.tt.getStoredMove(state, entries, state.ZobristKey)
        self.moveScores = [self.score_move(move, hashMove) for move in moves]
        ordered_moves = [m for _, m in sorted(zip(self.moveScores, moves), key = lambda pair : pair[0], reverse=True)]
        return ordered_moves

    @property
    def getCurrentMoveScores(self):
        return self.moveScores
