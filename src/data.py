'''

    TEMPEST_001, a didactic chess engine written in Python
    Copyright (C) 2022  Terry Nguyen (PyPioneer author)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''

# imports
from defs import squares, o

#                        EVALUATION                        #
# phase score
OPENING_PHASE_SCORE: int = 6192
ENDGAME_PHASE_SCORE: int = 518

# pawn bonuses and penalties
DOUBLED_PENALTY: int = 39

# positional score [phase][piece][square]

                                #                       OPENING                           #
positional_score: list = [[[    0,   0,   0,   0,   0,   0,  0,   0,    o, o, o, o, o, o, o, o,
                               98, 134,  61,  95,  68, 126, 34, -11,    o, o, o, o, o, o, o, o,
                               -6,   7,  26,  31,  65,  56, 25, -20,    o, o, o, o, o, o, o, o,
                              -14,  13,   6,  21,  23,  12, 17, -23,    o, o, o, o, o, o, o, o,
                              -27,  -2,  -5,  12,  17,   6, 10, -25,    o, o, o, o, o, o, o, o,
                              -26,  -4,  -4, -10,  -1,   3, 33, -12,    o, o, o, o, o, o, o, o,
                              -35,  -1, -20, -23, -15,  24, 38, -22,    o, o, o, o, o, o, o, o,
                                0,   0,   0,   0,   0,   0,  0,   0,    o, o, o, o, o, o, o, o],

                          [-167, -89, -34, -49,  61, -97, -15, -107,    o, o, o, o, o, o, o, o,
                            -73, -41,  72,  36,  23,  62,   7,  -17,    o, o, o, o, o, o, o, o,
                            -47,  60,  37,  65,  84, 129,  73,   44,    o, o, o, o, o, o, o, o,
                             -9,  17,  19,  53,  37,  69,  18,   22,    o, o, o, o, o, o, o, o,
                            -13,   4,  16,  13,  28,  19,  21,   -8,    o, o, o, o, o, o, o, o,
                            -23,  -9,  12,  10,  19,  17,  25,  -16,    o, o, o, o, o, o, o, o,
                            -29, -53, -12,  -3,  -1,  18, -14,  -19,    o, o, o, o, o, o, o, o,
                           -105, -21, -58, -33, -17, -28, -19,  -23,    o, o, o, o, o, o, o, o],

                          [  -29,   4, -82, -37, -25, -42,   7,  -8,    o, o, o, o, o, o, o, o,
                             -26,  16, -18, -13,  30,  59,  18, -47,    o, o, o, o, o, o, o, o,
                             -16,  37,  43,  40,  35,  50,  37,  -2,    o, o, o, o, o, o, o, o,
                              -4,   5,  19,  50,  37,  37,   7,  -2,    o, o, o, o, o, o, o, o,
                              -6,  13,  13,  26,  34,  12,  10,   4,    o, o, o, o, o, o, o, o,
                               0,  15,  15,  15,  14,  27,  18,  10,    o, o, o, o, o, o, o, o,
                               4,  16,  16,   0,   7,  21,  33,   1,    o, o, o, o, o, o, o, o,
                             -33,  -3, -14, -21, -13, -12, -39, -21,    o, o, o, o, o, o, o, o],

                          [     32,  42,  32,  51, 63,  9,  31,  43,    o, o, o, o, o, o, o, o,
                                27,  32,  58,  62, 80, 67,  26,  44,    o, o, o, o, o, o, o, o,
                                -5,  19,  26,  36, 17, 45,  61,  16,    o, o, o, o, o, o, o, o,
                               -24, -11,   7,  26, 24, 35,  -8, -20,    o, o, o, o, o, o, o, o,
                               -36, -26, -12,  -1,  9, -7,   6, -23,    o, o, o, o, o, o, o, o,
                               -45, -25, -16, -17,  3,  0,  -5, -33,    o, o, o, o, o, o, o, o,
                               -44, -16, -20,  -9, -1, 11,  -6, -71,    o, o, o, o, o, o, o, o,
                               -19, -13,   1,  17, 16,  7, -37, -26,    o, o, o, o, o, o, o, o],

                          [  -28,   0,  29,  12,  59,  44,  43,  45,    o, o, o, o, o, o, o, o,
                             -24, -39,  -5,   1, -16,  57,  28,  54,    o, o, o, o, o, o, o, o,
                             -13, -17,   7,   8,  29,  56,  47,  57,    o, o, o, o, o, o, o, o,
                             -27, -27, -16, -16,  -1,  17,  -2,   1,    o, o, o, o, o, o, o, o,
                              -9, -26,  -9, -10,  -2,  -4,   3,  -3,    o, o, o, o, o, o, o, o,
                             -14,   2, -11,  -2,  -5,   2,  14,   5,    o, o, o, o, o, o, o, o,
                             -35,  -8,  11,   2,   8,  15,  -3,   1,    o, o, o, o, o, o, o, o,
                              -1, -18,  -9,  10, -15, -25, -31, -50,    o, o, o, o, o, o, o, o],

                          [  -65,  23,  16, -15, -56, -34,   2,  13,    o, o, o, o, o, o, o, o,
                              29,  -1, -20,  -7,  -8,  -4, -38, -29,    o, o, o, o, o, o, o, o,
                              -9,  24,   2, -16, -20,   6,  22, -22,    o, o, o, o, o, o, o, o,
                             -17, -20, -12, -27, -30, -25, -14, -36,    o, o, o, o, o, o, o, o,
                             -49,  -1, -27, -39, -46, -44, -33, -51,    o, o, o, o, o, o, o, o,
                             -14, -14, -22, -46, -44, -30, -15, -27,    o, o, o, o, o, o, o, o,
                               1,   7,  -8, -64, -43, -16,   9,   8,    o, o, o, o, o, o, o, o,
                             -15,  36,  12, -54,   8, -28,  24,  14,    o, o, o, o, o, o, o, o]],


                            #                           ENDGAME                             #


                          [[   0,   0,   0,   0,   0,   0,   0,   0,    o, o, o, o, o, o, o, o,
                             178, 173, 158, 134, 147, 132, 165, 187,    o, o, o, o, o, o, o, o,
                              94, 100,  85,  67,  56,  53,  82,  84,    o, o, o, o, o, o, o, o,
                              32,  24,  13,   5,  -2,   4,  17,  17,    o, o, o, o, o, o, o, o,
                              13,   9,  -3,  -7,  -7,  -8,   3,  -1,    o, o, o, o, o, o, o, o,
                               4,   7,  -6,   1,   0,  -5,  -1,  -8,    o, o, o, o, o, o, o, o,
                              13,   8,   8,  10,  13,   0,   2,  -7,    o, o, o, o, o, o, o, o,
                               0,   0,   0,   0,   0,   0,   0,   0,    o, o, o, o, o, o, o, o],

                          [  -58, -38, -13, -28, -31, -27, -63, -99,    o, o, o, o, o, o, o, o,
                             -25,  -8, -25,  -2,  -9, -25, -24, -52,    o, o, o, o, o, o, o, o,
                             -24, -20,  10,   9,  -1,  -9, -19, -41,    o, o, o, o, o, o, o, o,
                             -17,   3,  22,  22,  22,  11,   8, -18,    o, o, o, o, o, o, o, o,
                             -18,  -6,  16,  25,  16,  17,   4, -18,    o, o, o, o, o, o, o, o,
                             -23,  -3,  -1,  15,  10,  -3, -20, -22,    o, o, o, o, o, o, o, o,
                             -42, -20, -10,  -5,  -2, -20, -23, -44,    o, o, o, o, o, o, o, o,
                             -31, -51, -23, -15, -22, -18, -50, -64,    o, o, o, o, o, o, o, o],

                          [   -14, -21, -11,  -8, -7,  -9, -17, -24,    o, o, o, o, o, o, o, o,
                               -8,  -4,   7, -12, -3, -13,  -4, -14,    o, o, o, o, o, o, o, o,
                                2,  -8,   0,  -1, -2,   6,   0,   4,    o, o, o, o, o, o, o, o,
                               -3,   9,  12,   9, 14,  10,   3,   2,    o, o, o, o, o, o, o, o,
                               -6,   3,  13,  19,  7,  10,  -3,  -9,    o, o, o, o, o, o, o, o,
                              -12,  -3,   8,  10, 13,   3,  -7, -15,    o, o, o, o, o, o, o, o,
                              -14, -18,  -7,  -1,  4,  -9, -15, -27,    o, o, o, o, o, o, o, o,
                              -23,  -9, -23,  -5, -9, -16,  -5, -17,    o, o, o, o, o, o, o, o],

                          [       13, 10, 18, 15, 12,  12,   8,   5,    o, o, o, o, o, o, o, o,
                                  11, 13, 13, 11, -3,   3,   8,   3,    o, o, o, o, o, o, o, o,
                                   7,  7,  7,  5,  4,  -3,  -5,  -3,    o, o, o, o, o, o, o, o,
                                   4,  3, 13,  1,  2,   1,  -1,   2,    o, o, o, o, o, o, o, o,
                                   3,  5,  8,  4, -5,  -6,  -8, -11,    o, o, o, o, o, o, o, o,
                                  -4,  0, -5, -1, -7, -12,  -8, -16,    o, o, o, o, o, o, o, o,
                                  -6, -6,  0,  2, -9,  -9, -11,  -3,    o, o, o, o, o, o, o, o,
                                  -9,  2,  3, -1, -5, -13,   4, -20,    o, o, o, o, o, o, o, o],

                          [   -9,  22,  22,  27,  27,  19,  10,  20,    o, o, o, o, o, o, o, o,
                             -17,  20,  32,  41,  58,  25,  30,   0,    o, o, o, o, o, o, o, o,
                             -20,   6,   9,  49,  47,  35,  19,   9,    o, o, o, o, o, o, o, o,
                               3,  22,  24,  45,  57,  40,  57,  36,    o, o, o, o, o, o, o, o,
                             -18,  28,  19,  47,  31,  34,  39,  23,    o, o, o, o, o, o, o, o,
                             -16, -27,  15,   6,   9,  17,  10,   5,    o, o, o, o, o, o, o, o,
                             -22, -23, -30, -16, -16, -23, -36, -32,    o, o, o, o, o, o, o, o,
                             -33, -28, -22, -43,  -5, -32, -20, -41,    o, o, o, o, o, o, o, o],

                          [  -74, -35, -18, -18, -11,  15,   4, -17,    o, o, o, o, o, o, o, o,
                             -12,  17,  14,  17,  17,  38,  23,  11,    o, o, o, o, o, o, o, o,
                              10,  17,  23,  15,  20,  45,  44,  13,    o, o, o, o, o, o, o, o,
                              -8,  22,  24,  27,  26,  33,  26,   3,    o, o, o, o, o, o, o, o,
                             -18,  -4,  21,  24,  27,  23,   9, -11,    o, o, o, o, o, o, o, o,
                             -19,  -3,  11,  21,  23,  16,   7,  -9,    o, o, o, o, o, o, o, o,
                             -27, -11,   4,  13,  14,   4,  -5, -17,    o, o, o, o, o, o, o, o,
                             -53, -34, -21, -11, -28, -14, -24, -43,    o, o, o, o, o, o, o, o],
]]

# mirror the board because there is no optimal way to flip the board, (no not the [::-1] or the numpy flip, board is a 1d array)
mirror_board: tuple = (
    squares['a1'], squares['b1'], squares['c1'], squares['d1'], squares['e1'], squares['f1'], squares['g1'], squares['h1'],         o, o, o, o, o, o, o, o,
    squares['a2'], squares['b2'], squares['c2'], squares['d2'], squares['e2'], squares['f2'], squares['g2'], squares['h2'],         o, o, o, o, o, o, o, o,
    squares['a3'], squares['b3'], squares['c3'], squares['d3'], squares['e3'], squares['f3'], squares['g3'], squares['h3'],         o, o, o, o, o, o, o, o,
    squares['a4'], squares['b4'], squares['c4'], squares['d4'], squares['e4'], squares['f4'], squares['g4'], squares['h4'],         o, o, o, o, o, o, o, o,
    squares['a5'], squares['b5'], squares['c5'], squares['d5'], squares['e5'], squares['f5'], squares['g5'], squares['h5'],         o, o, o, o, o, o, o, o,
    squares['a6'], squares['b6'], squares['c6'], squares['d6'], squares['e6'], squares['f6'], squares['g6'], squares['h6'],         o, o, o, o, o, o, o, o,
    squares['a7'], squares['b7'], squares['c7'], squares['d7'], squares['e7'], squares['f7'], squares['g7'], squares['h7'],         o, o, o, o, o, o, o, o,
    squares['a8'], squares['b8'], squares['c8'], squares['d8'], squares['e8'], squares['f8'], squares['g8'], squares['h8'],         o, o, o, o, o, o, o, o,
)

# piece value, 2d matrix because index opening phase and endgame phase
piece_val: tuple = (             [0, 82, 337, 365, 477, 1025, 0, -82, -337, -365, -477, -1025, 0],
                                [0, 94, 281, 297, 512,  936, 0, -94, -281, -297, -512,  -936, 0])

# self explanitory
phases: dict = {'opening':0, 'endgame':1, 'midgame':2}
