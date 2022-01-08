from Transpositions import TranspositionTable

piece_vals = {
    "K": 0,
    "Q": 2682,
    "R": 1380,
    "B": 915,
    "N": 854,
    "p": 206,
}

class MoveOrdering:
    def __init__(self):
        self.maxMoveCount = 218
        self.squareControlledByOppPenalty = 350
        self.capturedPieceMult = 10
        self.moveScores = []
        self.invalidMove = None
        self.tt = TranspositionTable()

    def score_move(self, state, move) -> int:
        score = 0
        movePieceType = move.pieceMoved
        movePieceCaptured = move.pieceCaptured

        if movePieceCaptured != '--':
            score = self.capturedPieceMult * piece_vals[movePieceCaptured[1]] - piece_vals[movePieceType[1]]

        if movePieceType[1] == 'p':
            if move.isPawnPromotion:
                score += piece_vals['Q']
        else:
            endSquare = (move.endRow, move.endCol)
            if endSquare in state.oppPawnAttackMap:
                score -= self.squareControlledByOppPenalty

        if move.castlemove:
            score += 100

        if move.isCapture:
            score += 50

        return score

    def OrderMoves(self, state, moves, entries):
        hashMove = self.tt.getStoredMove(state, entries, state.ZobristKey)

        self.moveScores = []
        for move in moves:
            score = self.score_move(state, move)

            if (move == hashMove):
                score += 10000

            self.moveScores.append(score)

        ordered_moves = self.SortMoves(moves)
        return ordered_moves

    def SortMoves(self, moves):
        for i in range(1, len(moves)):
            
            key = self.moveScores[i]
            moveKey = moves[i]

            j = i - 1
            
            while j >= 0 and key < self.moveScores[j]:
                moves[j + 1] = moves[j]
                self.moveScores[j + 1] = self.moveScores[j]
                j -= 1

            self.moveScores[j + 1] = key
            moves[j + 1] = moveKey
        return moves

    @property
    def getCurrentMoveScores(self):
        return self.moveScores
