import numpy as np

piece_value = {
    "K": 9999999,
    "Q": 900,
    "R": 500,
    "B": 320,
    "N": 300,
    "p": 100,
}

piece_map_visualization = {
    "K": np.array(
        [
            [2, 3, 1, 0, 0, 1, 3, 2],
            [2, 2, 0, 0, 0, 0, 2, 2],
            [-3, -4, -4, -5, -5, -4, -4, -3],
            [-3, -4, -4, -6, -6, -4, -4, -3],
            [-3, -4, -4, -6, -6, -4, -4, -3],
            [-3, -4, -4, -5, -5, -4, -4, -3],
            [2, 2, 0, 0, 0, 0, 2, 2],
            [2, 3, 1, 0, 0, 1, 3, 2],
        ]
    ),
    "Q": np.array(
        [
            [-20,-10,-10, -5, -5,-10,-10,-20],
			[-10,  0,  0,  0,  0,  0,  0,-10],
			[-10,  0,  5,  5,  5,  5,  0,-10],
			[-5,  0,  5,  5,  5,  5,  0, -5],
			[0,  0,  5,  5,  5,  5,  0, -5],
			[-10,  5,  5,  5,  5,  5,  0,-10],
			[-10,  0,  5,  0,  0,  0,  0,-10],
			[-20,-10,-10, -5, -5,-10,-10,-20]
        ]
    ),
    "R": np.array(
        [
            [0,  0,  0,  0,  0,  0,  0,  0],
			[5, 10, 10, 10, 10, 10, 10,  5],
			[-5,  0,  0,  0,  0,  0,  0, -5],
			[-5,  0,  0,  0,  0,  0,  0, -5],
			[-5,  0,  0,  0,  0,  0,  0, -5],
			[-5,  0,  0,  0,  0,  0,  0, -5],
			[-5,  0,  0,  0,  0,  0,  0, -5],
			[0,  0,  0,  5,  5,  0,  0,  0]
        ]
    ),
    "B": np.array(
        [
            [-20,-10,-10,-10,-10,-10,-10,-20],
			[-10,  0,  0,  0,  0,  0,  0,-10],
			[-10,  0,  5, 10, 10,  5,  0,-10],
			[-10,  5,  5, 10, 10,  5,  5,-10],
			[-10,  0, 10, 10, 10, 10,  0,-10],
			[-10, 10, 10, 10, 10, 10, 10,-10],
			[-10,  5,  0,  0,  0,  0,  5,-10],
			[-20,-10,-10,-10,-10,-10,-10,-20],
        ]
    ),
    "N": np.array(
        [
            [-50,-40,-30,-30,-30,-30,-40,-50],
			[-40,-20,  0,  0,  0,  0,-20,-40],
			[-30,  0, 10, 15, 15, 10,  0,-30],
			[-30,  5, 15, 20, 20, 15,  5,-30],
			[-30,  0, 15, 20, 20, 15,  0,-30],
			[-30,  5, 10, 15, 15, 10,  5,-30],
			[-40,-20,  0,  5,  5,  0,-20,-40],
			[-50,-40,-30,-30,-30,-30,-40,-50],
        ]
    ),
    "wp": np.array(
        [
            [0,  0,  0,  0,  0,  0,  0,  0],
			[50, 50, 50, 50, 50, 50, 50, 50],
			[10, 10, 20, 30, 30, 20, 10, 10],
			[5,  5, 10, 25, 25, 10,  5,  5],
			[0,  0,  0, 20, 20,  0,  0,  0],
			[5, -5,-10,  0,  0,-10, -5,  5],
			[5, 10, 10,-20,-20, 10, 10,  5],
			[0,  0,  0,  0,  0,  0,  0,  0]
        ]
    ),
}

piece_map_visualization['bp'] = np.flipud(piece_map_visualization['wp'])


class Evaluate:
    def __init__(self):
        self.endgameMaterialStart = piece_value["R"] * \
            2 + piece_value["B"] * piece_value['N']

    def countMaterial(self, state, colorIndex):
        board = state.board
        material = 0
        for row in range(len(board)):
            for col in range(len(board[row])):
                piece = board[row][col]
                if piece != "--":
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
        moppUpScore = 0
        if (myMaterial > oppMaterial + piece_value["p"] * 2) and endgameWeight > 0:
            friendKingSq = state.whiteKingLocation if friendIdx == 'w' else state.blackKingLocation
            oppKingSq = state.blackKingLocation if enemyIdx == 'b' else state.whiteKingLocation

    def ForceKingToCornerEndgameVal(self, friendKingSquare, oppKingSquare, endgameWeight):
        evaluation = 0

        oppKingRank = oppKingSquare[0]
        oppKingCol = oppKingSquare[1]

        oppKingDstFromCentreCol = max(3 - oppKingCol, oppKingCol - 4)
        oppKingDstFromCentreRank = max(3 - oppKingRank, oppKingRank - 4)
        oppKingDstFromCentre = (
            oppKingDstFromCentreCol + oppKingDstFromCentreRank)
        evaluation += oppKingDstFromCentre

        friendKingRank = friendKingSquare[0]
        friendKingCol = friendKingSquare[1]

        dstBetweenKingsRank = abs(friendKingRank - oppKingRank)
        dstBetweenKingsCol = abs(friendKingCol - oppKingCol)
        dstBetweenKings = dstBetweenKingsRank + dstBetweenKingsCol
        evaluation += 14 - dstBetweenKings

        return int(evaluation * 10 * endgameWeight)

    def endgamePhaseWeight(self, materialCountWithoutPawns):
        multiplier = 1 / self.endgameMaterialStart
        return 1 - min(1, materialCountWithoutPawns * multiplier)

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

        for row in range(len(state.board)):
            for col in range(len(state.board[row])):
                square = state.board[row, col]
                if square != "--":
                    if square[1] == "p":
                        if square[0] == "w":
                            pos_val = piece_map_visualization['wp'][row][col]
                            whiteEval += pos_val * 0.111
                        elif square[0] == "b":
                            pos_val = piece_map_visualization['bp'][row][col]
                            blackEval += pos_val * 0.111
                    else:
                        if square[0] == "w":
                            pos_val = piece_map_visualization[square[1]][row][col]
                            whiteEval += pos_val * 0.111
                        elif square[0] == "b":
                            reverse_map = np.flipud(piece_map_visualization[square[1]])
                            pos_val = reverse_map[row][col]
                            blackEval += pos_val * 0.111

        #print("BLACK MATERIAL:", blackMaterial)
        #print("WHITE MATERIAL:", whiteMaterial)

        eval, perspective = whiteEval - blackEval, 1 if state.whitesturn else -1
        return eval * perspective
