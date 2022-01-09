from pawn_evaluation import pawn_evaluation
import numpy as np

piece_value_mg = {
    "K": 32767,
    'Q': 2538,
    'R': 1276,
    'B': 825,
    'N': 781,
    'p': 124,
    '-': 0,
}

piece_value_eg = {
    'K': 32767,
    'Q': 2682,
    'R': 1380,
    'B': 915,
    'N': 854,
    'p': 206,
    '-': 0,
}

SAFETY_TABLE = {
    0,  0,   1,   2,   3,   5,   7,   9,  12,  15,
  18,  22,  26,  30,  35,  39,  44,  50,  56,  62,
  68,  75,  82,  85,  89,  97, 105, 113, 122, 131,
  140, 150, 169, 180, 191, 202, 213, 225, 237, 248,
  260, 272, 283, 295, 307, 319, 330, 342, 354, 366,
  377, 389, 401, 412, 424, 436, 448, 459, 471, 483,
  494, 500, 500, 500, 500, 500, 500, 500, 500, 500,
  500, 500, 500, 500, 500, 500, 500, 500, 500, 500,
  500, 500, 500, 500, 500, 500, 500, 500, 500, 500,
  500, 500, 500, 500, 500, 500, 500, 500, 500, 500
}

PIECE_SQUARE_TABLE = {
    'p': [
        9000,9000,9000,9000,9000,9000,9000,9000 ,
         200, 200, 200, 200, 200, 200, 200, 200 ,
         100, 100, 100, 100, 100, 100, 100, 100 ,
          40,  40,  90, 100, 100,  90,  40,  40 ,
          20,  20,  20, 100, 150,  20,  20,  20 ,
           2,   4,   0,  15,   4,   0,   4,   2 ,
         -10, -10, -10, -20, -35, -10, -10, -10 ,
           0,   0,   0,   0,   0,   0,   0,   0 
    ],

    'pEnd': [
        9000,9000,9000,9000,9000,9000,9000,9000 ,
          500, 500, 500, 500, 500, 500, 500, 500 ,
          300, 300, 300, 300, 300, 300, 300, 300 ,
           90,  90,  90, 100, 100,  90,  90,  90 ,
           70,  70,  70,  85,  85,  70,  70,  70 ,
           20,  20,  20,  20,  20,  20,  20,  20 , 
          -10, -10, -10, -10, -10, -10, -10, -10 ,
            0,   0,   0,   0,   0,   0,   0,   0 
    ],

    'KEnd': [
          20, -80, -60, -60, -60, -60, -80, -20 ,
         -80, -40,   0,   0,   0,   0, -40, -80 ,
         -60,   0,  20,  30,  30,  20,   0, -60 , 
         -60,  10,  30,  40,  40,  30,  10, -60 ,
         -60,   0,  30,  40,  40,  30,   0, -60 , 
         -60,  10,  20,  30,  30,  30,   1, -60 ,
         -80, -40,   0,  10,  10,   0,  -4, -80 ,
         -20, -80, -60, -60, -60, -60, -80, -20 ,
    ],

    'K': [
         -60, -80, -80, -2, -20, -80, -80, -60 ,
         -60, -80, -80, -2, -20, -80, -80, -60 ,
         -60, -80, -80, -2, -20, -80, -80, -60 ,
         -60, -80, -80, -2, -20, -80, -80, -60 ,
         -40, -60, -60, -8, -80, -60, -60, -40 ,
         -20, -40, -40, -40,-40, -40, -40, -20 ,
          40,  40,   0,   0,  0,   0,  40,  40 ,
          40,  60,  20,   0,  0,  20,  60,  40 
    ],

    'B': [
         -40, -20, -20, -20, -20, -20, -20, -40 ,
         -20,   0,   0,   0,   0,   0,   0, -20 ,
         -20,   0,  10,  20,  20,  10,   0, -20 ,
         -20,  10,  10,  20,  20,  10,  10, -20 ,
         -20,   0,  20,  20,  20,  20,   0, -20 ,
         -20,  20,  20,  20,  20,  20,  20, -20 ,
         -20,  10,   0,   0,   0,   0,  10, -20 ,
         -40, -20, -20, -20, -20, -20, -20, -40 
    ],

    'R': [
          0,  0,  0,  0,  0,  0,  0,   0 ,
          10, 20, 20, 20, 20, 20, 20,  10 ,
         -10,  0,  0,  0,  0,  0,  0, -10 ,
         -10,  0,  0,  0,  0,  0,  0, -10 ,
         -10,  0,  0,  0,  0,  0,  0, -10 ,
         -10,  0,  0,  0,  0,  0,  0, -10 , 
         -10,  0,  0,  0,  0,  0,  0, -10 ,
         -30, 30, 40, 10, 10,  0,  0, -30 
    ],

    'Q': [
         -40, -20, -20, -10, -10, -20, -20, -40 ,
         -20,   0,   0,   0,   0,   0,   0, -20 ,
         -20,   0,  10,  10,  10,  10,   0, -20 ,
         -10,   0,  10,  10,  10,  10,   0, -10 ,
           0,   0,  10,  10,  10,  10,   0, -10 ,
         -20,  10,  10,  10,  10,  10,   0, -20 ,
         -20,   0,  10,   0,   0,   0,   0, -20 ,
         -40, -20, -20, -10, -10, -20, -20, -40 
    ],

    'N': [
        -20, -80, -60, -60, -60, -60, -80, -20 ,
        -80, -40,   0,   0,   0,   0, -40, -80 ,
        -60,   0,  20,  30,  30,  20,   0, -60 , 
        -60,  10,  30,  40,  40,  30,  10, -60 ,
        -60,   0,  30,  40,  40,  30,   0, -60 , 
        -60,  10,  20,  30,  30,  30,   1, -60 ,
        -80, -40,   0,  10,  10,   0,  -4, -80 ,
        -20, -80, -60, -60, -60, -60, -80, -20 ,
    ]
}

class Evaluate:
    def __init__(self):
        self.eg = False
        self.pawn_util = pawn_evaluation()

    def material(self, state, colorIndex, eg):
        material = 0

        arr = piece_value_mg if not eg else piece_value_eg
        material += state.pieceCount[colorIndex + 'Q'] * arr['Q']
        material += state.pieceCount[colorIndex + 'R'] * arr['R']
        material += state.pieceCount[colorIndex + 'B'] * arr['B']
        material += state.pieceCount[colorIndex + 'N'] * arr['N']
        material += state.pieceCount[colorIndex + 'p'] * arr['p']

        return material

    def materialNoPawns(self, state, colorIndex, eg):
        material = 0

        arr = piece_value_mg if not eg else piece_value_eg
        material += state.pieceCount[colorIndex + 'Q'] * arr['Q']
        material += state.pieceCount[colorIndex + 'R'] * arr['R']
        material += state.pieceCount[colorIndex + 'B'] * arr['B']
        material += state.pieceCount[colorIndex + 'N'] * arr['N']

        return material

    def materialOnlyPawns(self, state, colorIndex, eg):
        material = 0

        arr = piece_value_mg if not eg else piece_value_eg
        material += state.pieceCount[colorIndex + 'p'] * arr['p']

        return material

    def psqt_bonus(self, state, rank, file, eg):
        square = state.board[rank][file]
        pieceType = square[1]
        position = (rank * 8 + file) if square[0] == 'w' else ((7 - rank) * 8 + file) 

        if not pieceType in ['K', 'p']:
            square_piece_tbl = PIECE_SQUARE_TABLE[pieceType]
            return square_piece_tbl[position]
        else:
            if not eg:
                square_piece_tbl = PIECE_SQUARE_TABLE[pieceType]
            else:
                square_piece_tbl = PIECE_SQUARE_TABLE[pieceType.join('End')]
            return square_piece_tbl[position]

    def psqt_(self, state, colorIndex, eg):
        v = 0
        for rank in range(len(state.board)):
            for file in range(len(state.board[rank])):
                if state.board[rank][file] != '--' \
                    and state.board[rank][file][0] == colorIndex:
                        v += self.psqt_bonus(state, rank, file, eg)
        return v
    
    def middle_game_eval(self, state, eg):
        v = 0

        v += (self.material(state, 'w', eg) - self.material(state, 'b', eg))
        v += (self.psqt_(state, 'w', eg) - self.psqt_(state, 'b', eg))

        perspective = 1 if state.whitesturn else -1
        return perspective * v

    def evaluate(self, state):
        return self.middle_game_eval(state, self.eg)

