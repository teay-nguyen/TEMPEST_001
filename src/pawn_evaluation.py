
class pawn_evaluation:
    def __init__(self):
        pass

    def isolated(self, state, side, rank, file):
        if state.board[rank][file] != (side + 'p'): return 0
        for row in range(8):
            if (state.board[row][file - 1]) == (side + 'p'): return 0
            if (state.board[row][file + 1]) == (side + 'p'): return 0
        return 1

    def disolated(self, state, side, rank, file):
        oppSide = 'b' if side == 'w' else 'w'
        if state.board[rank][file] != (side + 'p'): return 0
        if (self.isolated(state, side, rank, file)):
            obe, eop, ene = 0, 0, 0
            for row in range(8):
                if (row > rank & state.board[row][file] == (side + 'p')): obe += 1
                if (row < rank & state.board[row][file] == (oppSide + 'p')): eop += 1
                if (state.board[row][file - 1] == (oppSide + 'p'))\
                    | (state.board[row][file + 1] == (oppSide + 'p')): ene += 1
            if (obe > 0 & ene == 0 & eop > 0): return 1
        return 1

    def backward(self, state, side, rank, file):
        if side == 'w':
            if state.board[rank][file] != 'wp': return 0
            for row in range(8):
                if state.board[row, file - 1] == 'wp'\
                 | state.board[row, file + 1] == 'wp': return 0
            if state.board[rank - 2][file - 1] == 'bp'\
             | state.board[rank - 2][file + 1] == 'bp'\
             | state.board[rank - 1][file] == 'bp': return 1
            return 0
        elif side == 'b':
            if state.board[rank][file] != 'bp': return 0
            for row in range(8):
                if state.board[row, file - 1] == 'bp'\
                 | state.board[row, file + 1] == 'bp': return 0
            if state.board[rank + 2][file - 1] == 'wp'\
             | state.board[rank + 2][file + 1] == 'wp'\
             | state.board[rank + 1][file] == 'wp': return 1
            return 0

    def doubled(self, state, side, rank, file):
        if side == 'w':
            if state.board[rank][file] != 'wp': return 0
            if state.board[rank + 1][file] != 'wp': return 0
            if state.board[rank + 1][file - 1] == 'wp': return 0
            if state.board[rank + 1][file + 1] == 'wp': return 0
            return 1
        elif side == 'b':
            if state.board[rank][file] != 'bp': return 0
            if state.board[rank - 1][file] != 'bp': return 0
            if state.board[rank - 1][file - 1] == 'bp': return 0
            if state.board[rank - 1][file + 1] == 'bp': return 0
            return 1

    def pawns_mg(self, state, side):
        v = 0
        for rank in range(len(state.board)):
            for file in range(len(state.board[rank])):
                if state.board[rank][file] != (side + 'p'): continue
                if self.disolated(state, side, rank, file): v -= 11
                elif self.isolated(state, side, rank, file): v -= 5
                elif self.backward(state, side, rank, file): v -= 9
                if self.doubled(state, side, rank, file): v -= 11

        return v
