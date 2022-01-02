
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

            self.moveScores.append(score)

        filtered_moves = self.SortMoves(moves)
        return filtered_moves

    def SortMoves(self, moves):
        tempMoves = moves
        for i in range(len(tempMoves)):
            for j in range(i+1, len(tempMoves)):
                if self.moveScores[i] < self.moveScores[j]:
                    self.moveScores[i], self.moveScores[j] = self.moveScores[j], self.moveScores[i]
                    tempMoves[i], tempMoves[j] = tempMoves[j], tempMoves[i]

        return tempMoves

