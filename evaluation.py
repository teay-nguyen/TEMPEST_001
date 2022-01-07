from PrecomputedMoveData import PrecomputedMoveData

piece_value = {
    "K": 0,
    "Q": 2682,
    "R": 1380,
    "B": 915,
    "N": 854,
    "p": 206,
}

piece_map_visualization = {
    'p': ([
        0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5,  5, 10, 25, 25, 10,  5,  5,
        0,  0,  0, 20, 20,  0,  0,  0,
        0, -5,-10,-60,-60,-10, -5,  0,
        5, 10, 10,-20,-20, 10, 10,  5,
        0,  0,  0,  0,  0,  0,  0,  0
    ]),

    'N': ([
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50,
    ]),

    'B': ([
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10, 10, 10,  5,  5, 10, 10,-10,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -20,-10,-10,-10,-10,-10,-10,-20,
    ]),

    'R': ([
        0,  0,  0,  0,  0,  0,  0,  0,
        5, 10, 10, 10, 10, 10, 10,  5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        0,  0,  0,  5,  5,  0,  0,  0
    ]),

    'Q': ([
        -20,-10,-10, -5, -5,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5,  5,  5,  5,  0,-10,
         -5,  0,  5,  5,  5,  5,  0, -5,
          0,  0,  5,  5,  5,  5,  0, -5,
        -10,  5,  5,  5,  5,  5,  0,-10,
        -10,  0,  5,  0,  0,  0,  0,-10,
        -20,-10,-10, -5, -5,-10,-10,-20,
    ]),

    'K': ([
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -20,-30,-30,-40,-40,-30,-30,-20,
        -10,-20,-20,-20,-20,-20,-20,-10,
         20, 20,  0,  0,  0,  0, 20, 20,
         20, 30, 10,  0,  0, 10, 30, 20,
    ]),

    'KEnd': ([
        -50,-40,-30,-20,-20,-30,-40,-50,
        -30,-20,-10,  0,  0,-10,-20,-30,
        -30,-10, 20, 30, 30, 20,-10,-30,
        -30,-10, 30, 40, 40, 30,-10,-30,
        -30,-10, 30, 40, 40, 30,-10,-30,
        -30,-10, 20, 30, 30, 20,-10,-30,
        -30,-30,  0,  0,  0,  0,-30,-30,
        -50,-30,-30,-30,-30,-30,-30,-50
    ]),
}

CenterControlTable = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 50, 50, 15,  5,-30,
    -30,  0, 15, 50, 50, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]

class Evaluate:
    def __init__(self):
        self.preComputedMoveData = PrecomputedMoveData()
        self.endgameMaterialStart = (piece_value["R"] * 2) + piece_value["B"] + piece_value['N']
        self.isEG = False

    def ReadSquare(self, table, row, col, isWhite):
        if not isWhite:
            rank = 7 - row
            square = rank * 8 + col
        else:
            square = row * 8 + col

        return table[square]

    def bishop_pair(self, bishop_count):
        return True if bishop_count >= 2 else False

    def countMaterialNew(self, state, colorIndex: str) -> int:
        pieceCount = state.pieceCount
        material = 0

        material += piece_value['Q'] * pieceCount[colorIndex + 'Q']
        material += piece_value['R'] * pieceCount[colorIndex + 'R']
        material += piece_value['B'] * pieceCount[colorIndex + 'B']
        material += piece_value['N'] * pieceCount[colorIndex + 'N']
        material += piece_value['p'] * pieceCount[colorIndex + 'p']

        return material

    def countMaterialWithoutPawnsNew(self, state, colorIndex: str) -> int:
        pieceCount = state.pieceCount
        material = 0

        material += piece_value['Q'] * pieceCount[colorIndex + 'Q']
        material += piece_value['R'] * pieceCount[colorIndex + 'R']
        material += piece_value['B'] * pieceCount[colorIndex + 'B']
        material += piece_value['N'] * pieceCount[colorIndex + 'N']

        return material

    def mopUpEval(self, state, friendIdx, enemyIdx, myMaterial, oppMaterial, endgameWeight):
        mopUpScore = 0
        if (myMaterial > (oppMaterial + piece_value["p"] * 2)) and (endgameWeight > 0):
            friendKingSq = state.whiteKingLocation if friendIdx == 'w' else state.blackKingLocation
            oppKingSq = state.whiteKingLocation if enemyIdx == 'w' else state.blackKingLocation

            oppKingRank = oppKingSq[0]
            oppKingCol = oppKingSq[1]

            mopUpScore += self.preComputedMoveData.centreManhattonDistance[oppKingRank, oppKingCol] * 10
            mopUpScore += (14 - self.preComputedMoveData.NumRookMovesToReachSquare(friendKingSq, oppKingSq)) * 4

            return int(mopUpScore * 3 * endgameWeight)
        return 0

    def endgamePhaseWeight(self, materialCountWithoutPawns):
        multiplier = 1 / self.endgameMaterialStart
        return 1 - min(1, materialCountWithoutPawns * multiplier)

    def evalPieceSquareTbls(self, state, colorIndex, endgamePhaseWeight) -> float:
        score = 0

        if endgamePhaseWeight > .1:
            self.isEG = True
        else:
            self.isEG = False

        for row in range(len(state.board)):
            for col in range(len(state.board[row])):
                pieceSide = state.board[row][col][0]
                pieceType = state.board[row][col][1]
                if state.board[row][col] != '--' and pieceSide == colorIndex:
                    if pieceType != 'K':
                        if colorIndex == 'w':
                            pos_val = self.ReadSquare(piece_map_visualization[pieceType], row, col, True) + self.ReadSquare(CenterControlTable, row, col, True)
                            score += pos_val
                        elif colorIndex == 'b':
                            pos_val = self.ReadSquare(piece_map_visualization[pieceType], row, col, False) + self.ReadSquare(CenterControlTable, row, col, False)
                            score += pos_val

        if not self.isEG:
            if colorIndex == 'w':
                kingEarlyPhase = self.ReadSquare(piece_map_visualization['K'], state.whiteKingLocation[0], state.whiteKingLocation[1], True)
                score += int(kingEarlyPhase * (1 - endgamePhaseWeight))
            elif colorIndex == 'b':
                kingEarlyPhase = self.ReadSquare(piece_map_visualization['K'], state.blackKingLocation[0], state.blackKingLocation[1], False)
                score += int(kingEarlyPhase * (1 - endgamePhaseWeight))
        else:
            if colorIndex == 'w':
                kingEarlyPhase = self.ReadSquare(piece_map_visualization['KEnd'], state.whiteKingLocation[0], state.whiteKingLocation[1], True)
                score += int(kingEarlyPhase * (1 - endgamePhaseWeight))
            elif colorIndex == 'b':
                kingEarlyPhase = self.ReadSquare(piece_map_visualization['KEnd'], state.blackKingLocation[0], state.blackKingLocation[1], False)
                score += int(kingEarlyPhase * (1 - endgamePhaseWeight))

        if self.bishop_pair(state.pieceCount[colorIndex + 'B']): score += 50

        return score

    def evaluate(self, state, lowPerformanceMode) -> float:
        blackEval = 0
        whiteEval = 0

        if lowPerformanceMode:
            whiteEval += self.countMaterialNew(state, 'w')
            blackEval += self.countMaterialNew(state, 'b')
        else:
            whiteMaterial = self.countMaterialNew(state, 'w')
            blackMaterial = self.countMaterialNew(state, 'b')

            whiteMaterialWithoutPawns = self.countMaterialWithoutPawnsNew(state, 'w')
            blackMaterialWithoutPawns = self.countMaterialWithoutPawnsNew(state, 'b')
            whiteEndgamePhaseWeight = self.endgamePhaseWeight(whiteMaterialWithoutPawns)
            blackEndgamePhaseWeight = self.endgamePhaseWeight(blackMaterialWithoutPawns)

            whiteEval += whiteMaterial
            blackEval += blackMaterial

            whiteEval += self.mopUpEval(state, 'w', 'b', whiteMaterial, blackMaterial, whiteEndgamePhaseWeight)
            blackEval += self.mopUpEval(state, 'b', 'w', blackMaterial, whiteMaterial, blackEndgamePhaseWeight)

            whitePieceSquareTableEval = self.evalPieceSquareTbls(state, 'w', whiteEndgamePhaseWeight)
            blackPieceSquareTableEval = self.evalPieceSquareTbls(state, 'b', blackEndgamePhaseWeight)

            whiteEval += whitePieceSquareTableEval
            blackEval += blackPieceSquareTableEval
        
        eval = whiteEval - blackEval
        perspective = 1 if state.whitesturn else -1

        return eval * perspective
