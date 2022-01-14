from Transpositions import TranspositionTable
from psqt import setBasicValues

class MoveOrdering:
    def __init__(self):
        self.moveScores:list = []
        self.tt:TranspositionTable = TranspositionTable()
        self.basic_values:setBasicValues = setBasicValues()

    def score_move(self, move, hash_move):
        score:int = 0
        movePieceType:str = move.pieceMoved
        movePieceCaptured:str = move.pieceCaptured
        if movePieceCaptured != '--': score = (self.basic_values.piece_value[movePieceCaptured[1]] - self.basic_values.piece_value[movePieceType[1]])
        if move == hash_move: score += 100000
        return score

    def OrderMoves(self, state, moves, entries):
        hashMove = self.tt.getStoredMove(state, entries, state.ZobristKey)
        self.moveScores:list = [self.score_move(move, hashMove) for move in moves]
        ordered_moves:list = [m for _, m in sorted(zip(self.moveScores, moves), key=lambda pair:pair[0], reverse = True)]
        return ordered_moves

    @property
    def getCurrentMoveScores(self):
        return self.moveScores
