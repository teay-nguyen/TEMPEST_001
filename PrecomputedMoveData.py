import numpy as np


class PrecomputedMoveData:
    def __init__(self):
        self.centreManhattonDistance = np.zeros((8, 8))
        self.orthogonalDistance = np.zeros((8, 8, 8, 8))
        self.kingDistance = np.zeros((8, 8, 8, 8))

        for row1 in range(8):
            for col1 in range(8):
                fileDstFromCentre = max(3 - col1, col1 - 4)
                rankDstFromCentre = max(3 - row1, row1 - 4)
                self.centreManhattonDistance[row1, col1] = fileDstFromCentre + rankDstFromCentre

                for row2 in range(8):
                    for col2 in range(8):
                        rankDistance = abs(row1 - row2)
                        fileDistance = abs(col1 - col2)
                        self.orthogonalDistance[row1, col1, row2, col2] = fileDistance + rankDistance
                        self.kingDistance[row1, col1, row2, col2] = max(fileDistance, rankDistance)

    def NumRookMovesToReachSquare(self, startSquare, targetSquare):
        return self.orthogonalDistance[startSquare[0], startSquare[1], targetSquare[0], targetSquare[1]]
