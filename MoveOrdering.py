
piece_vals = {
    "K": 0,
    "Q": 950,
    "R": 500,
    "B": 350,
    "N": 310,
    "p": 100,
}

class MoveOrdering:
    def __init__(self):
        self.maxMoveCount = 218
        self.squareControlledByOppPenalty = 350
        self.capturedPieceMult = 10
        self.moveScores = []
        self.invalidMove = None

    def OrderMoves(self, state, moves):
        self.moveScores = []
        for move in moves:
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
