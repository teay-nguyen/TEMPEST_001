from Transpositions import TranspositionTable
from psqt import MVV_LVA, INDEX_MVV_LVA

class MoveOrdering:
    def __init__(self):
        self.maxMoveCount = 218
        self.squareControlledByOppPenalty = 350
        self.capturedPieceMult = 10
        self.moveScores = []
        self.invalidMove = None
        self.tt = TranspositionTable()

    def score_move(self, move, hash_move) -> int:
        score = 0
        movePieceType = move.pieceMoved
        movePieceCaptured = move.pieceCaptured

        score += MVV_LVA[INDEX_MVV_LVA[movePieceCaptured[1]]][INDEX_MVV_LVA[movePieceType[1]]]
        if move == hash_move: score += 10000

        return score

    def OrderMoves(self, state, moves, entries):
        hashMove = self.tt.getStoredMove(state, entries, state.ZobristKey)
        self.moveScores = [self.score_move(move, hashMove) for move in moves]
        ordered_moves = self.SortMoves(moves)
        return ordered_moves

    def SortMoves(self, moves):
        for i in range(len(moves)):
            for j in range(i+1, len(moves)):
                if self.moveScores[i] < self.moveScores[j]:
                    moves[i], moves[j] = moves[j], moves[i]
                    self.moveScores[i], self.moveScores[j] = self.moveScores[j], self.moveScores[i]
        return moves

    @property
    def getCurrentMoveScores(self):
        return self.moveScores
