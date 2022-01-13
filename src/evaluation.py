from psqt import setBasicValues
from verification_util import verify_sq
from Transpositions import TranspositionTable

class Pawn:
    def __init__(self):
        self.basic_values = setBasicValues()

    def isolated(self, state, row, col, side):
        if state.board[row][col][1] != 'p': return 0
        side_pawn = side + 'p'
        for y in range(8):
            if (verify_sq(y, col - 1)) and (state.board[y][col - 1] == side_pawn): return 0
            if (verify_sq(y, col + 1)) and (state.board[y][col + 1] == side_pawn): return 0
        return 1

    def doubled_isolated(self, state, row, col, side):
        if state.board[row][col][1] != 'p': return 0
        side_pawn = side + 'p'
        opp_pawn = 'bp' if side == 'w' else 'wp'
        if (self.isolated(state, row, col, side)):
            obe, eop, ene = 0, 0, 0
            for y in range(8):
                if (y > row and state.board[y][col] == side_pawn): obe += 1
                if (y < row and state.board[y][col] == opp_pawn): eop += 1
                if (verify_sq(y, col - 1) and state.board[y][col - 1] == opp_pawn)\
                    | (verify_sq(y, col + 1) and state.board[y][col + 1] == opp_pawn): ene += 1
            if (obe > 0 and ene == 0 and eop > 0): return 1
        return 0

    def backward(self, state, row, col, side):
        if state.board[row][col][1] != 'p': return 0
        side_pawn = side + 'p'
        opp_pawn = 'bp' if side == 'w' else 'wp'
        if side == 'w':
            for y in range(8):
                if (verify_sq(y, col - 1) and state.board[y][col - 1] == side_pawn)\
                    | (verify_sq(y, col + 1) and state.board[y][col + 1] == side_pawn): return 0
            if (verify_sq(row - 2, col - 1) and state.board[row - 2][col - 1] == opp_pawn)\
                | (verify_sq(row - 2, col + 1) and state.board[row - 2][col + 1] == opp_pawn)\
                | (verify_sq(row - 1, col) and state.board[row - 1][col] == opp_pawn): return 1
            return 0
        elif side == 'b':
            for y in range(8):
                if (verify_sq(y, col - 1) and state.board[y][col - 1] == side_pawn)\
                    | (verify_sq(y, col + 1) and state.board[y][col + 1] == side_pawn): return 0
            if (verify_sq(row + 2, col - 1) and state.board[row + 2][col - 1] == opp_pawn)\
                | (verify_sq(row + 2, col + 1) and state.board[row + 2][col + 1] == opp_pawn)\
                | (verify_sq(row + 1, col) and state.board[row + 1][col] == opp_pawn): return 1
            return 0
        return 0

    def doubled(self, state, row, col, side):
        if state.board[row][col][1] != 'p': return 0
        side_pawn = side + 'p'
        if side == 'w':
            if (verify_sq(row + 1, col) and state.board[row + 1][col] != side_pawn): return 0
            if (verify_sq(row + 1, col - 1) and state.board[row + 1][col - 1] == side_pawn): return 0
            if (verify_sq(row + 1, col + 1) and state.board[row + 1][col + 1] == side_pawn): return 0
            return 1
        elif side == 'b':
            if (verify_sq(row - 1, col) and state.board[row - 1][col] != side_pawn): return 0
            if (verify_sq(row - 1, col - 1) and state.board[row - 1][col - 1] == side_pawn): return 0
            if (verify_sq(row - 1, col + 1) and state.board[row - 1][col + 1] == side_pawn): return 0
            return 1
        return 0

    def pawn_total_mg(self, state, side):
        v = 0
        for row in range(8):
            for col in range(8):
                if (self.doubled_isolated(state, row, col, side)): v -= 24
                elif (self.isolated(state, row, col, side)): v -= 10
                elif (self.backward(state, row, col, side)): v -= 20
                v -= self.doubled(state, row, col, side) * 15

        return v

class Pieces:
    def __init__(self):
        self.basic_values = setBasicValues()

class Evaluate:
    def __init__(self):
        self.basic_values = setBasicValues()
        self.tt = TranspositionTable()
        self.pawn_eval = Pawn()
        self.tt_entries = self.tt.init_entries()

    def materialTotal(self, state, colorIndex):
        material = 0
        arr = self.basic_values.piece_value
        material += state.pieceCount[colorIndex + 'Q'] * arr['Q']
        material += state.pieceCount[colorIndex + 'R'] * arr['R']
        material += state.pieceCount[colorIndex + 'B'] * arr['B']
        material += state.pieceCount[colorIndex + 'N'] * arr['N']
        material += state.pieceCount[colorIndex + 'p'] * arr['p']
        return material

    def materialNoPawns(self, state, colorIndex):
        material = 0
        arr = self.basic_values.piece_value
        material += state.pieceCount[colorIndex + 'Q'] * arr['Q']
        material += state.pieceCount[colorIndex + 'R'] * arr['R']
        material += state.pieceCount[colorIndex + 'B'] * arr['B']
        material += state.pieceCount[colorIndex + 'N'] * arr['N']
        return material

    def materialOnlyPawns(self, state, colorIndex):
        arr = self.basic_values.piece_value
        return state.pieceCount[colorIndex + 'p'] * arr['p']

    def psqt_bonus(self, state, rank, file, t):
        square = state.board[rank][file]
        pieceType = square[1]
        position = (rank * 8 + file) if square[0] == 'w' else ((7 - rank) * 8 + file) 
        return t[pieceType][position]

    def psqt_(self, state, colorIndex, t):
        v = 0
        for rank in range(len(state.board)):
            for file in range(len(state.board[rank])):
                if state.board[rank][file] != '--' \
                    and state.board[rank][file][0] == colorIndex:
                        v += self.psqt_bonus(state, rank, file, t)
        return v
    
    def main_eval(self, state):
        res = self.tt.getStoredScore(state, self.tt_entries)
        if res != None:
            return res if state.whitesturn else -res

        result, eg_score, mg_score = 0, 0, 0
        stronger, weaker = None, None

        mg_score = self.materialTotal(state, 'w') + self.psqt_(state, 'w', self.basic_values.psqt_mg)\
                    - self.materialTotal(state, 'b') - self.psqt_(state, 'b', self.basic_values.psqt_mg)
        eg_score = self.materialTotal(state, 'w') + self.psqt_(state, 'w', self.basic_values.psqt_eg)\
                    - self.materialTotal(state, 'b') - self.psqt_(state, 'b', self.basic_values.psqt_eg)

        if state.whitesturn:
            result += self.basic_values.tempo
        else:
            result -= self.basic_values.tempo

        if (state.pieceCount['wB'] > 1): result += self.basic_values.bishop_pair
        if (state.pieceCount['bB'] > 1): result -= self.basic_values.bishop_pair
        if (state.pieceCount['wN'] > 1): result += self.basic_values.knight_pair
        if (state.pieceCount['bN'] > 1): result -= self.basic_values.knight_pair
        if (state.pieceCount['wR'] > 1): result += self.basic_values.rook_pair
        if (state.pieceCount['bR'] > 1): result -= self.basic_values.rook_pair

        res = result + mg_score
        self.tt.storeScore(state, self.tt_entries, res)

        return res if state.whitesturn else -res

    def evaluate(self, state):
        return self.main_eval(state)

