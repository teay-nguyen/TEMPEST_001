import numpy as np


class PrecomputedMoveData:
    def __init__(self):
        self.centreManhattonDistance = np.zeros(64)
        self.orthogonalDistance = np.zeros((64, 64))
        self.kingDistance = np.zeros((64, 64))

        for row1 in range(8):
            for col1 in range(8):
                coordA = row1 * 8 + col1
                fileDstFromCentre = max(3 - col1, col1 - 4)
                rankDstFromCentre = max(3 - row1, row1 - 4)
                self.centreManhattonDistance[coordA] = fileDstFromCentre + rankDstFromCentre

                for row2 in range(8):
                    for col2 in range(8):
                        coordB = row2 * 8 + col2
                        rankDistance = abs(row1 - row2)
                        fileDistance = abs(col1 - col2)
                        self.orthogonalDistance[coordA, coordB] = fileDistance + rankDistance
                        self.kingDistance[coordA, coordB] = max(fileDistance, rankDistance)

    def NumRookMovesToReachSquare(self, startSquare, targetSquare) -> int:
        return self.orthogonalDistance[startSquare[0] * 8 + startSquare[1]][targetSquare[0] * 8 + targetSquare[1]]
