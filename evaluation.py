import numpy as np
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

    'KMiddle': ([
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

KingDirections = [
    (-1, 0),
    (-1, 1),
    (-1, -1),
    (1, 0),
    (1, -1),
    (1, 1),
    (0, 1),
    (0, -1),
]

class Evaluate:
    def __init__(self):
        self.preComputedMoveData = PrecomputedMoveData()
        self.endgameMaterialStart = (piece_value["R"] * 2) + piece_value["B"] + piece_value['N']

        self.whiteKingSquareAttack = np.zeros(64)
        self.blackKingSquareAttack = np.zeros(64)


    def ReadSquare(self, table, row, col, isWhite):
        if not isWhite:
            rank = 7 - row
            square = rank * 8 + col
        else:
            square = row * 8 + col

        return table[square]

    def countMaterial(self, state, colorIndex: str) -> int:
        board = state.board
        material = 0
        for row in range(len(board)):
            for col in range(len(board[row])):
                piece = board[row][col]
                if piece != "--":
                    if piece[0] == colorIndex:
                        material += piece_value[piece[1]]

        return material

    def countMaterialWithoutPawns(self, state, colorIndex: str) -> int:
        board = state.board
        material = 0
        for row in range(len(board)):
            for col in range(len(board[row])):
                piece = board[row][col]
                if piece != "--" and piece[1] != "p":
                    if piece[0] == colorIndex:
                        material += piece_value[piece[1]]

        return material

    def generateKingAttackHeatMap(self, state):
        whiteKingLocation = state.whiteKingLocation
        blackKingLocation = state.blackKingLocation
        for i in range(8):
            rank, file = KingDirections[i][0], KingDirections[i][1]
            whiteKingRank, whiteKingFile = whiteKingLocation[0], whiteKingLocation[1]
            blackKingRank, blackKingFile = blackKingLocation[0], blackKingLocation[1]

            squareAroundWhiteKing = (whiteKingRank + rank, whiteKingFile + file)
            squareAroundBlackKing = (blackKingRank + rank, blackKingFile + file)

            passCriteria = [
                0 <= squareAroundWhiteKing[0] < 8,
                0 <= squareAroundWhiteKing[1] < 8,
                0 <= squareAroundBlackKing[0] < 8,
                0 <= squareAroundBlackKing[1] < 8,

            ]

            if all(passCriteria):
                squareAroundWhiteKingIdx = squareAroundWhiteKing[0] * 8 + squareAroundWhiteKing[1]
                squareAroundBlackKingIdx = squareAroundBlackKing[0] * 8 + squareAroundBlackKing[1]

                self.whiteKingSquareAttack[squareAroundWhiteKingIdx] = 20
                self.blackKingSquareAttack[squareAroundBlackKingIdx] = 20

    def mopUpEval(self, state, friendIdx, enemyIdx, myMaterial, oppMaterial, endgameWeight):
        mopUpScore = 0
        if (myMaterial > (oppMaterial + piece_value["p"] * 2)) and (endgameWeight > 0):

            friendKingSq = state.whiteKingLocation if friendIdx == 'w' else state.blackKingLocation
            oppKingSq = state.whiteKingLocation if enemyIdx == 'w' else state.blackKingLocation

            oppKingRank = oppKingSq[0]
            oppKingCol = oppKingSq[1]

            mopUpScore += self.preComputedMoveData.centreManhattonDistance[oppKingRank, oppKingCol] * 10
            mopUpScore += (14 - self.preComputedMoveData.NumRookMovesToReachSquare(friendKingSq, oppKingSq)) * 4

            return int(mopUpScore * endgameWeight)
        return 0

    def endgamePhaseWeight(self, materialCountWithoutPawns):
        multiplier = 1 / self.endgameMaterialStart
        return 1 - min(1, materialCountWithoutPawns * multiplier)

    def evalPieceSquareTbls(self, state, colorIndex, endgamePhaseWeight) -> float:
        self.generateKingAttackHeatMap(state)
        score = 0
        for row in range(len(state.board)):
            for col in range(len(state.board[row])):
                pieceSide = state.board[row][col][0]
                pieceType = state.board[row][col][1]
                if state.board[row][col] != '--' and pieceSide == colorIndex:
                    if pieceType != 'K':

                        if colorIndex == 'w':
                            pos_val = self.ReadSquare(piece_map_visualization[pieceType], row, col, True) + self.ReadSquare(CenterControlTable, row, col, True)
                            kingAttackSquare = self.ReadSquare(self.blackKingSquareAttack, row, col, True)
                            score += pos_val + kingAttackSquare

                        elif colorIndex == 'b':
                            pos_val = self.ReadSquare(piece_map_visualization[pieceType], row, col, False) + self.ReadSquare(CenterControlTable, row, col, False)
                            kingAttackSquare = self.ReadSquare(self.whiteKingSquareAttack, row, col, False)
                            score += pos_val + kingAttackSquare
                    else:
                        if colorIndex == 'w':
                            pos_val = self.ReadSquare(piece_map_visualization[pieceType], row, col, True) + self.ReadSquare(CenterControlTable, row, col, True)
                            score += int(pos_val * (1 - endgamePhaseWeight))

                        elif colorIndex == 'b':
                            pos_val = self.ReadSquare(piece_map_visualization[pieceType], row, col, False) + self.ReadSquare(CenterControlTable, row, col, False)
                            score += int(pos_val * (1 - endgamePhaseWeight))

        return score

    def evaluate(self, state, lowPerformanceMode) -> float:
        blackEval = 0
        whiteEval = 0

        if lowPerformanceMode:
            whiteEval += self.countMaterial(state, 'w')
            blackEval += self.countMaterial(state, 'b')
        else:
            whiteMaterial = self.countMaterial(state, 'w')
            blackMaterial = self.countMaterial(state, 'b')

            whiteMaterialWithoutPawns = self.countMaterialWithoutPawns(state, 'w')
            blackMaterialWithoutPawns = self.countMaterialWithoutPawns(state, 'b')
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
