import numpy as np
from PrecomputedMoveData import PrecomputedMoveData

piece_value = {
    "K": 0,
    "Q": 950,
    "R": 500,
    "B": 350,
    "N": 310,
    "p": 100,
}

piece_map_visualization = {
    'p': np.array([
        0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5,  5, 10, 25, 25, 10,  5,  5,
        0,  0,  0, 20, 20,  0,  0,  0,
        5, -5,-10,  0,  0,-10, -5,  5,
        5, 10, 10,-20,-20, 10, 10,  5,
        0,  0,  0,  0,  0,  0,  0,  0
    ]),

    'N': np.array([
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50,
    ]),

    'B': np.array([
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -20,-10,-10,-10,-10,-10,-10,-20,
    ]),

    'R': np.array([
        0,  0,  0,  0,  0,  0,  0,  0,
        5, 10, 10, 10, 10, 10, 10,  5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        0,  0,  0,  5,  5,  0,  0,  0
    ]),

    'Q': np.array([
        -20,-10,-10, -5, -5,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5,  5,  5,  5,  0,-10,
        -5,  0,  5,  5,  5,  5,  0, -5,
        0,  0,  5,  5,  5,  5,  0, -5,
        -10,  5,  5,  5,  5,  5,  0,-10,
        -10,  0,  5,  0,  0,  0,  0,-10,
        -20,-10,-10, -5, -5,-10,-10,-20
    ]),

    'KMiddle': np.array([
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -20,-30,-30,-40,-40,-30,-30,-20,
        -10,-20,-20,-20,-20,-20,-20,-10,
        20, 20,  0,  0,  0,  0, 20, 20,
        20, 30, 10,  0,  0, 10, 30, 20
    ]),

    'KEnd': np.array([
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

class Evaluate:
    def __init__(self):
        self.preComputedMoveData = PrecomputedMoveData()
        self.endgameMaterialStart = (piece_value["R"] * 2) + piece_value["B"] + piece_value['N']

    def ReadSquare(self, table, row, col):
        square = row * 8 + col
        return table[square]

    def countMaterial(self, state, colorIndex):
        board = state.board
        material = 0
        for piece in np.nditer(board):
            if piece != "--":
                piece = str(piece)
                if colorIndex == "w":
                    if piece[0] == "w":
                        material += piece_value[piece[1]]
                elif colorIndex == "b":
                    if piece[0] == "b":
                        material += piece_value[piece[1]]

        return material

    def countMaterialWithoutPawns(self, state, colorIndex):
        board = state.board
        material = 0
        for row in range(len(board)):
            for col in range(len(board[row])):
                piece = board[row][col]
                if piece != "--" and piece[1] != "p":
                    if colorIndex == "w":
                        if piece[0] == "w":
                            material += piece_value[piece[1]]
                    elif colorIndex == "b":
                        if piece[0] == "b":
                            material += piece_value[piece[1]]

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

            return int(mopUpScore * endgameWeight)

        return 0

    def endgamePhaseWeight(self, materialCountWithoutPawns):
        multiplier = 1 / self.endgameMaterialStart
        return 1 - min(1, materialCountWithoutPawns * multiplier)

    def evalPieceSquareTbls(self, state, colorIndex, endgamePhaseWeight):
        score = 0
        for row in range(len(state.board)):
            for col in range(len(state.board[row])):
                pieceSide = state.board[row][col][0]
                pieceType = state.board[row][col][1]
                if state.board[row][col] != '--' and pieceSide == colorIndex:
                    if pieceType != 'K':
                        if colorIndex == 'w':
                            pos_val = self.ReadSquare(piece_map_visualization[pieceType], row, col)
                            score += pos_val
                        elif colorIndex == 'b':
                            reverse_map = np.flipud(piece_map_visualization[pieceType])
                            pos_val = self.ReadSquare(reverse_map, row, col)
                            score += pos_val
                    else:
                        if colorIndex == 'w':
                            pos_val = self.ReadSquare(piece_map_visualization['KMiddle'], row, col)
                            score += int(pos_val * (1 - endgamePhaseWeight))
                        elif colorIndex == 'b':
                            reverse_map = np.flipud(piece_map_visualization['KMiddle'])
                            pos_val = self.ReadSquare(reverse_map, row, col)
                            score += int(pos_val * (1 - endgamePhaseWeight))

        return score

    def evaluate(self, state):
        blackEval = 0
        whiteEval = 0

        whiteMaterial = self.countMaterial(state, 'w')
        blackMaterial = self.countMaterial(state, 'b')

        whiteMaterialWithoutPawns = self.countMaterialWithoutPawns(state, 'w')
        blackMaterialWithoutPawns = self.countMaterialWithoutPawns(state, 'b')
        whiteEndgamePhaseWeight = self.endgamePhaseWeight(
            whiteMaterialWithoutPawns)
        blackEndgamePhaseWeight = self.endgamePhaseWeight(
            blackMaterialWithoutPawns)

        whiteEval += whiteMaterial
        blackEval += blackMaterial

        whiteEval += self.mopUpEval(state, 'w', 'b', whiteMaterial,
                                    blackMaterial, whiteEndgamePhaseWeight)
        blackEval += self.mopUpEval(state, 'b', 'w', blackMaterial,
                                    whiteMaterial, blackEndgamePhaseWeight)

        whitePieceSquareTableEval = self.evalPieceSquareTbls(
            state, 'w', whiteEndgamePhaseWeight)
        blackPieceSquareTableEval = self.evalPieceSquareTbls(
            state, 'b', blackEndgamePhaseWeight)

        whiteEval += whitePieceSquareTableEval
        blackEval += blackPieceSquareTableEval

        #print("BLACK MATERIAL:", blackMaterial)
        #print("WHITE MATERIAL:", whiteMaterial)

        eval = whiteEval - blackEval
        perspective = 1 if state.whitesturn else -1

        return eval * perspective
