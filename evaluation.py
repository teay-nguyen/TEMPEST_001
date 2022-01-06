import numpy as np
from PrecomputedMoveData import PrecomputedMoveData

piece_value = {
    "K": 0,
    "Q": 2538,
    "R": 1276,
    "B": 825,
    "N": 781,
    "p": 124,
}

piece_map_visualization = {
    'p': ([
        0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5,  5, 10, 25, 25, 10,  5,  5,
        0,  0,  0, 20, 20,  0,  0,  0,
        5, -5,-10,-60,-60,-10, -5,  5,
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
        -10, 10,  0,  0,  0,  0, 10,-10,
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
        -20,-10,-10, -5, -5,-10,-10,-20
    ]),

    'KMiddle': ([
        0,  0,   .1,   .2,   .3,   .5,   .7,   .9,
        1.8,  2.2,  2.6,  3.0,  3.5,  3.9,  4.4,  5,
        6.8,  7.5,  8.2,  8.5,  8.9,  9.7, 10.5, 11.3,
        14.0, 15.0, 16.9, 18.0, 19.1, 20.2, 21.3, 22.5,
        26.0, 27.2, 28.3, 29.5, 30.7, 31.9, 33.0, 34.2,
        37.7, 38.9, 40.1, 41.2, 42.4, 43.6, 44.8, 45.9,
        49, 50, 50, 50, 50, 50, 50, 50,
        50, 50, 50, 50, 50, 50, 50, 50,
        50, 50, 50, 50, 50, 50, 50, 50,
        50, 50, 20, 20, 20, 20, 50, 50,
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

        self.whiteKingSquareAttack = np.array([
                    0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0,
            ])
        
        self.blackKingSquareAttack = np.array([
                    0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0,
            ])


    def ReadSquare(self, table, row, col):
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
        for direction in KingDirections:
            rank, file = direction[0], direction[1]
            whiteKingRank, whiteKingFile = whiteKingLocation[0], whiteKingLocation[1]
            blackKingRank, blackKingFile = blackKingLocation[0], blackKingLocation[1]

            squareAroundWhiteKing = (whiteKingRank + rank, whiteKingFile + file)
            squareAroundBlackKing = (blackKingRank + rank, blackKingFile + file)

            passCriteria = [
                squareAroundWhiteKing[0] <= 7,
                squareAroundWhiteKing[0] >= 0,
                squareAroundWhiteKing[1] <= 7,
                squareAroundWhiteKing[1] >= 0,

                squareAroundBlackKing[0] <= 7,
                squareAroundBlackKing[0] >= 0,
                squareAroundBlackKing[1] <= 7,
                squareAroundBlackKing[1] >= 0,

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

            return int(mopUpScore * 10 * endgameWeight)

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
                            pos_val = self.ReadSquare(piece_map_visualization[pieceType], row, col) + self.ReadSquare(CenterControlTable, row, col)
                            kingAttackSquare = self.ReadSquare(self.blackKingSquareAttack, row, col)
                            score += pos_val + kingAttackSquare

                        elif colorIndex == 'b':
                            reverse_map = piece_map_visualization[pieceType][::-1]
                            pos_val = self.ReadSquare(reverse_map, row, col) + self.ReadSquare(CenterControlTable, row, col)
                            kingAttackSquare = self.ReadSquare(self.blackKingSquareAttack, row, col)
                            score += pos_val + kingAttackSquare
                    else:
                        if colorIndex == 'w':
                            pos_val = self.ReadSquare(piece_map_visualization['KMiddle'], row, col) + self.ReadSquare(CenterControlTable, row, col)
                            score += int(pos_val * (1 - endgamePhaseWeight))

                        elif colorIndex == 'b':
                            reverse_map = piece_map_visualization['KMiddle'][::-1]
                            pos_val = self.ReadSquare(reverse_map, row, col) + self.ReadSquare(CenterControlTable, row, col)
                            score += int(pos_val * (1 - endgamePhaseWeight))

        return score

    def evaluate(self, state, lowPerformanceMode) -> float:
        blackEval = 0
        whiteEval = 0
        pieceMovedPenalties = ['Q','K','R']

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

        CastlePenalty = 100

        if state.whitesturn:
            whiteEval += CastlePenalty
        else:
            blackEval += CastlePenalty

        if state.inCheck():
            if state.whitesturn:
                whiteEval -= CastlePenalty
            else:
                blackEval -= CastlePenalty

        if not state.currCastleRights.wks:
            whiteEval -= CastlePenalty
        else:
            whiteEval += CastlePenalty

        if not state.currCastleRights.wqs:
            whiteEval -= CastlePenalty
        else:
            whiteEval += CastlePenalty

        if not state.currCastleRights.bks:
            blackEval -= CastlePenalty
        else:
            blackEval += CastlePenalty

        if not state.currCastleRights.bqs:
            blackEval -= CastlePenalty
        else:
            blackEval += CastlePenalty

        if len(state.moveLog) <= 10:
            if state.moveLog[-1] in pieceMovedPenalties:
                if state.moveLog[-1].pieceMoved[0] == 'w':
                    whiteEval -= 50
                elif state.moveLog[-1].pieceMoved[0] == 'b':
                    blackEval -= 50

        eval = whiteEval - blackEval
        perspective = 1 if state.whitesturn else -1

        return eval * perspective
