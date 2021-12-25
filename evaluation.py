import numpy as np

piece_value = {
    "K": 0,
    "Q": 10,
    "R": 5,
    "B": 3,
    "N": 3,
    "p": 1,
}

piece_map_visualization = {
    "K": np.array(
        [
            [2, 3, 1, 0, 0, 1, 3, 2],
            [2, 2, 0, 0, 0, 0, 2, 2],
            [-3, -4, -4, -5, -5, -4, -4, -3],
            [-3, -4, -4, -5, -5, -4, -4, -3],
            [-3, -4, -4, -5, -5, -4, -4, -3],
            [-3, -4, -4, -5, -5, -4, -4, -3],
            [2, 2, 0, 0, 0, 0, 2, 2],
            [2, 3, 1, 0, 0, 1, 3, 2],
        ]
    ),
    "Q": np.array(
        [
            [-2, -1, -1, -0.5, -0.5, -1, -1, -2],
            [-1, 0, 0, 0, 0, 0, 0, -1],
            [-1, 0.5, 0.5, 0.5, 0.5, 0.5, 0, -1],
            [-0.5, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5],
            [-0.5, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5],
            [-1, 0.5, 0.5, 0.5, 0.5, 0.5, 0, -1],
            [-1, 0, 0, 0, 0, 0, 0, -1],
            [-2, -1, -1, -0.5, -0.5, -1, -1, -2],
        ]
    ),
    "R": np.array(
        [
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0.5, 1, 1, 1, 1, 1, 1, 0.5],
            [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
            [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
            [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
            [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
            [0.5, 1, 1, 1, 1, 1, 1, 0.5],
            [0, 0, 0, 1, 1, 0, 0, 0],
        ]
    ),
    "B": np.array(
        [
            [-2, -1, -1, -1, -1, -1, -1, -2],
            [-1, 0, 0, 0, 0, 0, 0, -1],
            [-1, 0, 0.5, 1, 1, 0.5, 0, -1],
            [-1, 0.5, 0.5, 1, 1, 0.5, 0.5, -1],
            [-1, 0, 1, 1, 1, 1, 0, -1],
            [-1, 1, 1, 1, 1, 1, 1, -1],
            [-1, 1, 0, 0, 0, 0, 1, -1],
            [-2, -1, -1, -1, -1, -1, -1, -2],
        ]
    ),
    "N": np.array(
        [
            [-1, -0.5, 0, 0, 0, 0, -0.5, -1],
            [-0.5, 0.5, 1, 1, 1, 1, 0.5, -0.5],
            [0, 1, 1.5, 1.5, 1.5, 1.5, 1, 0],
            [0, 0.5, 1.5, 2, 2, 1.5, 0.5, 0],
            [0, 0.5, 1.5, 2, 2, 1.5, 0.5, 0],
            [0, 1, 1.5, 1.5, 1.5, 1.5, 1, 0],
            [-0.5, 0.5, 1, 1, 1, 1, 0.5, -0.5],
            [-1, -0.5, 0, 0, 0, 0, -0.5, -1],
        ]
    ),
    "wp": np.array(
        [
            [7, 8, 8, 8, 8, 8, 8, 7],
            [5, 5, 5, 5, 5, 5, 5, 5],
            [1, 1, 2, 3, 3, 2, 1, 1],
            [0.5, 0.5, 1, 2.5, 2.5, 1, 0.5, 0.5],
            [0, 0, 2, 3, 3, 2, 0, 0],
            [1, 1, 1, 0, 0, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ]
    ),
    "bp": np.array(
        [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 0, 0, 1, 1, 1],
            [0, 0, 2, 3, 3, 2, 0, 0],
            [0.5, 0.5, 1, 2.5, 2.5, 1, 0.5, 0.5],
            [1, 1, 2, 3, 3, 2, 1, 1],
            [5, 5, 5, 5, 5, 5, 5, 5],
            [7, 8, 8, 8, 8, 8, 8, 7],
        ]
    ),
}


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

    def engamePhaseWeight(self, materialCountWithoutPawns):
        multiplier = 1 / self.endgameMaterialStart
        return 1 - min(1, materialCountWithoutPawns * multiplier)

    def evaluate(self, state):
        blackEval = 0
        whiteEval = 0

        whiteMaterial, blackMaterial = self.countMaterial(
            state, "w"), self.countMaterial(state, "b")

        whiteEval += whiteMaterial
        blackEval += blackMaterial

        for row in range(len(state.board)):
            for col in range(len(state.board[row])):
                square = state.board[row, col]
                if square != "--":
                    if square[1] == "p":
                        if square[0] == "w":
                            pos_val = piece_map_visualization['wp'][row][col]
                            whiteEval += pos_val * 0.2
                        elif square[0] == "b":
                            pos_val = piece_map_visualization['bp'][row][col]
                            blackEval += pos_val * 0.2
                    else:
                        if square[0] == "w":
                            pos_val = piece_map_visualization[square[1]][row][col]
                            whiteEval += pos_val * 0.2
                        elif square[0] == "b":
                            pos_val = piece_map_visualization[square[1]][row][col]
                            blackEval += pos_val * 0.2

        #print("BLACK MATERIAL:", blackMaterial)
        #print("WHITE MATERIAL:", whiteMaterial)

        eval, perspective = whiteEval - blackEval, 1 if state.whitesturn else -1
        return eval * perspective
