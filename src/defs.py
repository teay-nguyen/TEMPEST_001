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

# constants
NAME: str = "TEMPEST_001" # name of the chess engine
ENGINE_VERSION: str = "v0.4 HashHobo [Terry Nguyen]" # commit version and author
ENGINE_STATUS: str = "WIP [WORK IN PROGRESS]" # engine status
BOARD_SQ_NUM: int = 0x80 # max number of squares in a 0x88 board
GEN_STACK: int = 0x100 # max number of moves in 1 position
PIECE_TYPES: int = 0xD # number of piece types: from empty to black king
CASTLE_VAL: int = 0x10 # max castle value
IDS: int = 0x2

# capture flags (just give em random number)
ALL_MOVES: int = 0x15ff
CAPTURE_MOVES: int = 0x15cc

# state storing
class move_t:
    def __init__(self, move_):
        self.move:int = move_
        self.score:int = 0

# mapping values to match coordinates or into strings
squares: dict = {
      "a8":0,   "b8":1,   "c8":2,   "d8":3,   "e8":4,   "f8":5,   "g8":6,   "h8":7,
     "a7":16,  "b7":17,  "c7":18,  "d7":19,  "e7":20,  "f7":21,  "g7":22,  "h7":23,
     "a6":32,  "b6":33,  "c6":34,  "d6":35,  "e6":36,  "f6":37,  "g6":38,  "h6":39,
     "a5":48,  "b5":49,  "c5":50,  "d5":51,  "e5":52,  "f5":53,  "g5":54,  "h5":55,
     "a4":64,  "b4":65,  "c4":66,  "d4":67,  "e4":68,  "f4":69,  "g4":70,  "h4":71,
     "a3":80,  "b3":81,  "c3":82,  "d3":83,  "e3":84,  "f3":85,  "g3":86,  "h3":87,
     "a2":96,  "b2":97,  "c2":98,  "d2":99, "e2":100, "f2":101, "g2":102, "h2":103,
    "a1":112, "b1":113, "c1":114, "d1":115, "e1":116, "f1":117, "g1":118, "h1":119,     "OFFBOARD":120,
}

# tuple for converting board coordinates into string
square_to_coords: tuple = (
    "a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8", "i8", "j8", "k8", "l8", "m8", "n8", "o8", "p8",
    "a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7", "i7", "j7", "k7", "l7", "m7", "n7", "o7", "p7",
    "a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6", "i6", "j6", "k6", "l6", "m6", "n6", "o6", "p6",
    "a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5", "i5", "j5", "k5", "l5", "m5", "n5", "o5", "p5",
    "a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4", "i4", "j4", "k4", "l4", "m4", "n4", "o4", "p4",
    "a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3", "i3", "j3", "k3", "l3", "m3", "n3", "o3", "p3",
    "a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2", "i2", "j2", "k2", "l2", "m2", "n2", "o2", "p2",
    "a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1", "i1", "j1", "k1", "l1", "m1", "n1", "o1", "p1",
)

# piece encoding
e, P, N, B, R, Q, K, p, n, b, r, q, k, o = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13
ascii_pieces: str = ".PNBRQKpnbrqko"
unicode_pieces: str = ".♙♘♗♖♕♔♙♞♝♜♛♚" # only used with CPython

# castling rights
castling_rights: tuple = (
     7, 15, 15, 15,  3, 15, 15, 11,     o, o, o, o, o, o, o, o,
    15, 15, 15, 15, 15, 15, 15, 15,     o, o, o, o, o, o, o, o,
    15, 15, 15, 15, 15, 15, 15, 15,     o, o, o, o, o, o, o, o,
    15, 15, 15, 15, 15, 15, 15, 15,     o, o, o, o, o, o, o, o,
    15, 15, 15, 15, 15, 15, 15, 15,     o, o, o, o, o, o, o, o,
    15, 15, 15, 15, 15, 15, 15, 15,     o, o, o, o, o, o, o, o,
    15, 15, 15, 15, 15, 15, 15, 15,     o, o, o, o, o, o, o, o,
    13, 15, 15, 15, 12, 15, 15, 14,     o, o, o, o, o, o, o, o,
)

# conversion into string or int, primarily for print
char_pieces: dict = { 'P':P, 'N':N, 'B':B, 'R':R, 'Q':Q, 'K':K, 'p':p, 'n':n, 'b':b, 'r':r, 'q':q, 'k':k }
int_pieces: dict = { P:'P', N:'N', B:'B', R:'R', Q:'Q', K:'K', p:'p', n:'n', b:'b', r:'r', q:'q', k:'k' }
promoted_pieces: dict = { Q:'q', R:'r', B:'b', N:'n', q:'q', r:'r', b:'b', n:'n' }

#    source, target params must be a valid value from the "squares" dict
#    for example: squares['d6']

# required utilities
encode_move = lambda source, target, piece, capture, pawn, enpassant, castling:                                                                                   \
              (source)                                                        |                                                                                   \
              (target << 7)                                                   |                                                                                   \
              (piece << 14)                                                   |                                                                                   \
              (capture << 18)                                                 |                                                                                   \
              (pawn << 19)                                                    |                                                                                   \
              (enpassant << 20)                                               |                                                                                   \
              (castling << 21)                                                                                                                                    \

# only used on moves applied with encode_move
get_move_source = lambda move: move & 0x7f
get_move_target = lambda move: (move >> 7) & 0x7f
get_move_promoted = lambda move: (move >> 14) & 0xf
get_move_capture = lambda move: (move >> 18) & 0x1
get_move_pawn = lambda move: (move >> 19) & 0x1
get_move_enpassant = lambda move: (move >> 20) & 0x1
get_move_castling = lambda move: (move >> 21) & 0x1

# board utility
get_row = lambda sq: sq >> 4
get_col = lambda sq: sq & 7
same_row = lambda sq1, sq2: get_row(sq1) == get_row(sq2)
same_col = lambda sq1, sq2: get_col(sq1) == get_col(sq2)

# initial values
sides: dict = { 'black':0, 'white':1 }
castling_vals: dict = { 'K':1, 'Q':2, 'k':4, 'q':8 }

# fen debug positions
start_position: str = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
empty_board: str = '8/8/8/8/8/8/8/8 w - - 0 1'
tricky_position: str = 'r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - '
preset_positions:dict = {
    'start_position':start_position,
    'empty_board': empty_board,
    'tricky_position': tricky_position,
}

# piece movement offsets
knight_offsets: tuple = (33, 31, 18, 14, -33, -31, -18, -14)
bishop_offsets: tuple = (15, 17, -15, -17)
rook_offsets: tuple = (16, -16, 1, -1)
king_offsets: tuple = (16, -16, 1, -1, 15, 17, -15, -17)

# misc
def print_move(move:int):
    if get_move_promoted(move):
        print('{}{}{}'.format(
                square_to_coords[get_move_source(move)],
                square_to_coords[get_move_target(move)],
                promoted_pieces[get_move_promoted(move)],
        ), end=' ')
    else:
        print('{}{}'.format(
                square_to_coords[get_move_source(move)],
                square_to_coords[get_move_target(move)],
        ), end=' ')
