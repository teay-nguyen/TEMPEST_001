import numpy as np

class PrecomputedMoveData:
    def __init__(self):
        self.ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
        self.rowsToRanks = {v: k for k, v in self.ranksToRows.items()}
        self.filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
        self.colsToFiles = {v: k for k, v in self.filesToCols.items()}

    def calculateOrthogonalDistance(self):
        orthogonalDistance = np.zeros((64, 64))
        kingDistance = np.zeros((64, 64))
        centerManhattanDistance = np.zeros(64)

        for squareA in range(64):
            pass