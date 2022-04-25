#!/usr/bin/env pypy3 -u

'''
                                        The TEMPEST Chess Engine
                                       (0x88 Board Representation)
                                                  by
                                               HashHobo


    - 0x88 board representation
    - I have not decided what kind of search algorithm to use yet, but I'm more inclined into choosing AlphaBeta or Monte-Carlo
    - Zobrist Hashing and Transposition Tables (I'm not sure if this is necessary in Monte-Carlo search)
    - I will attempt to implement a few search pruning techniques

                                 [LANGUAGE: PYTHON 3.8.9, VERSION: v2.1]

    - The engine is obviously weaker than other popular engines because I'm a rookie in writing powerful chess engines, so don't expect superb performance
    - I actually document or keep my older implementations of this, so you can check it out and probably send a PR if you want
    - I put the first version in the old trash implementation folder because it is indeed trash and doesn't work anyway
    - My old version was largely imcompatible with Pypy because Pypy somehow runs incredibly slow with my old version, maybe its because of pygame or just my trash coding skills
'''

# imports
from timing import timer
from time import perf_counter
import copy
import __future__

# stopwatch
convert_to_ms = lambda x : round(x * 1000)

# piece encoding
e, P, N, B, R, Q, K, p, n, b, r, q, k, o = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13
ascii_pieces:str = ".PNBRQKpnbrqko"
unicode_pieces:str = ".♙♘♗♖♕♔♙♞♝♜♛♚" # only used with CPython

# castling rights
castling_rights:list = [
      7, 15, 15, 15,  3, 15, 15, 11,  o, o, o, o, o, o, o, o,
     15, 15, 15, 15, 15, 15, 15, 15,  o, o, o, o, o, o, o, o,
     15, 15, 15, 15, 15, 15, 15, 15,  o, o, o, o, o, o, o, o,
     15, 15, 15, 15, 15, 15, 15, 15,  o, o, o, o, o, o, o, o,
     15, 15, 15, 15, 15, 15, 15, 15,  o, o, o, o, o, o, o, o,
     15, 15, 15, 15, 15, 15, 15, 15,  o, o, o, o, o, o, o, o,
     15, 15, 15, 15, 15, 15, 15, 15,  o, o, o, o, o, o, o, o,
     13, 15, 15, 15, 12, 15, 15, 14,  o, o, o, o, o, o, o, o
]

# mapping values to match coordinates or into strings
squares:dict = {
    "a8":0, "b8":1, "c8":2, "d8":3, "e8":4, "f8":5, "g8":6, "h8":7,
    "a7":16, "b7":17, "c7":18, "d7":19, "e7":20, "f7":21, "g7":22, "h7":23,
    "a6":32, "b6":33, "c6":34, "d6":35, "e6":36, "f6":37, "g6":38, "h6":39,
    "a5":48, "b5":49, "c5":50, "d5":51, "e5":52, "f5":53, "g5":54, "h5":55,
    "a4":64, "b4":65, "c4":66, "d4":67, "e4":68, "f4":69, "g4":70, "h4":71,
    "a3":80, "b3":81, "c3":82, "d3":83, "e3":84, "f3":85, "g3":86, "h3":87,
    "a2":96, "b2":97, "c2":98, "d2":99, "e2":100, "f2":101, "g2":102, "h2":103,
    "a1":112, "b1":113, "c1":114, "d1":115, "e1":116, "f1":117, "g1":118, "h1":119, "null_sq":120}

# tuple for converting board coordinates into string
square_to_coords:tuple = (
    "a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8", "i8", "j8", "k8", "l8", "m8", "n8", "o8", "p8",
    "a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7", "i7", "j7", "k7", "l7", "m7", "n7", "o7", "p7",
    "a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6", "i6", "j6", "k6", "l6", "m6", "n6", "o6", "p6",
    "a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5", "i5", "j5", "k5", "l5", "m5", "n5", "o5", "p5",
    "a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4", "i4", "j4", "k4", "l4", "m4", "n4", "o4", "p4",
    "a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3", "i3", "j3", "k3", "l3", "m3", "n3", "o3", "p3",
    "a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2", "i2", "j2", "k2", "l2", "m2", "n2", "o2", "p2",
    "a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1", "i1", "j1", "k1", "l1", "m1", "n1", "o1", "p1")

# conversion into string or int, primarily for print
char_pieces:dict = {'P':P, 'N':N, 'B':B, 'R':R, 'Q':Q, 'K':K, 'p':p, 'n':n, 'b':b, 'r':r, 'q':q, 'k':k}
promoted_pieces:dict = {Q:'q', R:'r', B:'b', N:'n', q:'q', r:'r', b:'b', n:'n'}

#    source, target params must be a valid value from the "squares" dict
#    for example: squares['d6']

# required utilities
encode_move = lambda source, target, piece, capture, pawn, enpassant, castling:                                             \
              (source)                  |                                                                                   \
              (target << 7)             |                                                                                   \
              (piece << 14)             |                                                                                   \
              (capture << 18)           |                                                                                   \
              (pawn << 19)              |                                                                                   \
              (enpassant << 20)         |                                                                                   \
              (castling << 21)                                                                                              \

get_move_source = lambda move : (move & 0x7f)
get_move_target = lambda move : ((move >> 7) & 0x7f)
get_move_piece = lambda move : ((move >> 14) & 0xf)
get_move_capture = lambda move : ((move >> 18) & 0x1)
get_move_pawn = lambda move : ((move >> 19) & 0x1)
get_move_enpassant = lambda move : ((move >> 20) & 0x1)
get_move_castling = lambda move : ((move >> 21) & 0x1)

# initial values
sides:dict = {'white':1, 'black':0}
castling:dict = {'K':1, 'Q':2, 'k':4, 'q':8}
capture_flags:dict = {"all_moves":32313132, "only_captures":12353231} # very specific keys

# fen debug positions
start_position:str = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
custom_endgame_position:str = '8/5R2/8/k7/1r6/4K3/6R1/8 w - - 0 1'
custom_middlegame_position:str = 'r1bq1rk1/ppp1bppp/2n2n2/3pp3/2BPP3/2N1BN2/PP3PPP/R2Q1RK1 w - - 0 1'
empty_board:str = '8/8/8/8/8/8/8/8 w - - 0 1'
tricky_position:str = 'r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1'

# piece movement offsets
knight_offsets:tuple = (33, 31, 18, 14, -33, -31, -18, -14)
bishop_offsets:tuple = (15, 17, -15, -17)
rook_offsets:tuple = (16, -16, 1, -1)
king_offsets:tuple = (16, -16, 1, -1, 15, 17, -15, -17)

# deep copy of arbitrary objects
full_cpy = lambda obj: copy.deepcopy(obj)





# used for storing moves and debugging
class moves_struct:
    def __init__(self) -> None:
        self.moves:list = [None for _ in range(256)]
        self.count:int = 0

# main driver
class board:
    def __init__(self) -> None:
        self.conv_rf_idx = lambda rank, file: (rank * 16) + file
        self.nodes:int = 0
        self.timer:timer = timer()
        self.parsed_fen:str = ''
        self.king_square:list = [squares['e8'], squares['e1']]
        self.side:int = -1
        self.castle:int = 15
        self.enpassant:int = squares['null_sq']
        self.board:list = [ # initialized with the start position so things can be easier
            r, n, b, q, k, b, n, r,     o, o, o, o, o, o, o, o,
            p, p, p, p, p, p, p, p,     o, o, o, o, o, o, o, o,
            e, e, e, e, e, e, e, e,     o, o, o, o, o, o, o, o,
            e, e, e, e, e, e, e, e,     o, o, o, o, o, o, o, o,
            e, e, e, e, e, e, e, e,     o, o, o, o, o, o, o, o,
            e, e, e, e, e, e, e, e,     o, o, o, o, o, o, o, o,
            P, P, P, P, P, P, P, P,     o, o, o, o, o, o, o, o,
            R, N, B, Q, K, B, N, R,     o, o, o, o, o, o, o, o]

    def clear_board(self) -> None:
        # sweep the surface clean
        for rank in range(8):
            for file in range(16):
                square = self.conv_rf_idx(rank, file)
                if (not (square & 0x88)):
                    self.board[square] = e
        self.side = -1
        self.castle = 0
        self.enpassant = squares['null_sq']

    def parse_fen(self, fen:str) -> None:
        # clear board before parsing string
        self.clear_board()

        # load pieces onto board
        self.parsed_fen = fen
        fen_segments = fen.split()
        fen_pieces = fen_segments[0]
        rank, file = 0, 0

        for sym in fen_pieces:
            if sym == '/':
                file = 0
                rank += 1
            else:
                if sym.isdigit():
                    assert int(sym) >= 0 and int(sym) <= 9
                    file += int(sym)
                else:
                    assert (ord('a') <= ord(sym) <= ord('z')) or (ord('A') <= ord(sym) <= ord('Z')) # unorthodoxed method to check FEN string but it works
                    square = self.conv_rf_idx(rank, file)
                    if (not (square & 0x88)):
                        if (sym == 'K'):
                            self.king_square[sides['white']] = square
                        elif (sym == 'k'): self.king_square[sides['black']] = square
                        self.board[square] = char_pieces[sym]
                        file += 1

        # choose which side goes first
        fen_side = fen_segments[1]
        if fen_side == 'w':
            self.side = sides['white']
        elif fen_side == 'b':
            self.side = sides['black']
        else: self.side = -1

        # castle rights parsing
        fen_castle = fen_segments[2]
        for sym in fen_castle:
            if sym == 'K': self.castle |= castling['K']
            if sym == 'Q': self.castle |= castling['Q']
            if sym == 'k': self.castle |= castling['k']
            if sym == 'q': self.castle |= castling['q']
            if sym == '-': break

        # load enpassant square
        fen_ep = fen_segments[3]
        if fen_ep != '-':
            file = ord(fen_ep[0]) - ord('a')
            rank = 8 - (ord(fen_ep[1]) - ord('0'))
            self.enpassant = self.conv_rf_idx(rank, file)
        else: self.enpassant = squares['null_sq']







    def xray_attacks(self, square:int, side:int):
        # bishop and queen
        for i in range(4):
            target_sq = square + bishop_offsets[i]
            while (not (target_sq & 0x88)):
                if 0 <= target_sq <= 127:
                    target_piece = self.board[target_sq]
                    if ((target_piece == B or target_piece == Q) if side else (target_piece == b or target_piece == q)): return 1
                    target_sq += bishop_offsets[i]

        # rook and queen
        for i in range(4):
            target_sq = square + rook_offsets[i]
            while (not (target_sq & 0x88)):
                if 0 <= target_sq <= 127:
                    target_piece = self.board[target_sq]
                    if ((target_piece == R or target_piece == Q) if side else (target_piece == r or target_piece == q)): return 1
                    target_sq += rook_offsets[i]

    def is_square_attacked(self, square:int, side:int) -> int:
        # pawn attacks
        if (side):
            if (not ((square + 17) & 0x88) and (self.board[square + 17] == P)): return 1
            if (not ((square + 15) & 0x88) and (self.board[square + 15] == P)): return 1
        else:
            if (not ((square - 17) & 0x88) and (self.board[square - 17] == p)): return 1
            if (not ((square - 15) & 0x88) and (self.board[square - 15] == p)): return 1

        # knight attacks
        for i in range(8):
            target_sq = square + knight_offsets[i]
            if 0 <= target_sq <= 127:
                target_piece = self.board[target_sq]
                if (not (target_sq & 0x88)):
                    if ((target_piece == N) if side else (target_piece == n)): return 1

        # king attacks
        for i in range(8):
            target_sq = square + king_offsets[i]
            if 0 <= target_sq <= 127:
                target_piece = self.board[target_sq]
                if (not (target_sq & 0x88)):
                    if ((target_piece == K) if side else (target_piece == k)): return 1

        # bishop attacks
        for i in range(4):
            target_sq = square + bishop_offsets[i]
            while (not (target_sq & 0x88)):
                if 0 <= target_sq <= 127:
                    target_piece = self.board[target_sq]
                    if ((target_piece == B or target_piece == Q) if side else (target_piece == b or target_piece == q)): return 1
                    if (target_piece): break
                    target_sq += bishop_offsets[i]

        # rook attacks
        for i in range(4):
            target_sq = square + rook_offsets[i]
            while (not (target_sq & 0x88)):
                if 0 <= target_sq <= 127:
                    target_piece = self.board[target_sq]
                    if ((target_piece == R or target_piece == Q) if side else (target_piece == r or target_piece == q)): return 1
                    if (target_piece): break
                    target_sq += rook_offsets[i]
        return 0








    def make_move(self, move:int, capture_flag:int):

        # filter out the None moves
        if move == None: return 0

        # quiet moves
        if (capture_flag == capture_flags['all_moves']):
            # copy stuff
            board_cpy = full_cpy(self.board)
            side_cpy = full_cpy(self.side)
            enpassant_cpy = full_cpy(self.enpassant)
            castle_cpy = full_cpy(self.castle)
            king_square_cpy = full_cpy(self.king_square)

            # get move source and the square it moves to
            from_square = get_move_source(move)
            to_square = get_move_target(move)
            promoted_piece = get_move_piece(move)
            enpass = get_move_enpassant(move)
            double_push = get_move_pawn(move)
            castling = get_move_castling(move)

            # perform the move
            self.board[to_square] = self.board[from_square]
            self.board[from_square] = e

            # adjusting board state
            if (promoted_piece): self.board[to_square] = promoted_piece
            if (enpass): self.board[(to_square + 16) if self.side else (to_square - 16)] = e
            self.enpassant = squares['null_sq']
            if (double_push): self.enpassant = (to_square + 16) if self.side else (to_square - 16)
            if (castling):
                if (to_square == squares['g1']):
                    self.board[squares['f1']] = self.board[squares['h1']]
                    self.board[squares['h1']] = e
                elif (to_square == squares['c1']):
                    self.board[squares['d1']] = self.board[squares['a1']]
                    self.board[squares['a1']] = e
                elif (to_square == squares['g8']):
                    self.board[squares['f8']] = self.board[squares['h8']]
                    self.board[squares['h8']] = e
                elif (to_square == squares['c8']):
                    self.board[squares['d8']] = self.board[squares['a8']]
                    self.board[squares['a8']] = e

            # update king square
            if (self.board[to_square] == K or self.board[to_square] == k): self.king_square[self.side] = to_square

            # update castling rights
            self.castle &= castling_rights[from_square]
            self.castle &= castling_rights[to_square]

            # change sides
            self.side ^= 1

            # take back move if king is under attack
            if (self.is_square_attacked(self.king_square[self.side ^ 1], self.side)):
                self.board = full_cpy(board_cpy)
                self.side = full_cpy(side_cpy)
                self.enpassant = full_cpy(enpassant_cpy)
                self.castle = full_cpy(castle_cpy)
                self.king_square = full_cpy(king_square_cpy)

                return 0 # illegal
            else: return 1 # legal
        elif capture_flag == capture_flags['only_captures']:
            if (get_move_capture(move)):
                self.make_move(move, capture_flags['all_moves'])
            else: return 0 # move is not a capture

    def add_move(self, move_list:moves_struct, move:int) -> None:
        move_list.moves[move_list.count] = move
        move_list.count += 1

    def gen_moves(self, move_list:moves_struct) -> None:
        move_list.count = 0
        for sq in range(128):
            if (not (sq & 0x88)):
                if (self.side):
                    if self.board[sq] == P:
                        to_sq = sq - 16
                        if (not (to_sq & 0x88)) and (not self.board[to_sq]):
                            if (sq >= squares['a7'] and sq <= squares['h7']):
                                self.add_move(move_list, encode_move(sq, to_sq, Q, 0, 0, 0, 0))
                                self.add_move(move_list, encode_move(sq, to_sq, R, 0, 0, 0, 0))
                                self.add_move(move_list, encode_move(sq, to_sq, B, 0, 0, 0, 0))
                                self.add_move(move_list, encode_move(sq, to_sq, N, 0, 0, 0, 0))
                            else:
                                self.add_move(move_list, encode_move(sq, to_sq, 0, 0, 0, 0, 0))
                                if ((sq >= squares['a2'] and sq <= squares['h2']) and (not self.board[sq - 32])):
                                    self.add_move(move_list, encode_move(sq, sq - 32, 0, 0, 1, 0, 0))
                        for i in range(4):
                            pawn_offset = bishop_offsets[i]
                            if (pawn_offset < 0):
                                to_sq = sq + pawn_offset
                                if (not (to_sq & 0x88)):
                                    if (sq >= squares['a7'] and sq <= squares['h7']) and\
                                        (self.board[to_sq] >= 7 and self.board[to_sq] <= 12):
                                        self.add_move(move_list, encode_move(sq, to_sq, Q, 1, 0, 0, 0))
                                        self.add_move(move_list, encode_move(sq, to_sq, R, 1, 0, 0, 0))
                                        self.add_move(move_list, encode_move(sq, to_sq, B, 1, 0, 0, 0))
                                        self.add_move(move_list, encode_move(sq, to_sq, N, 1, 0, 0, 0))
                                    else:
                                        if (self.board[to_sq] >= 7 and self.board[to_sq] <= 12):
                                            self.add_move(move_list, encode_move(sq, to_sq, 0, 1, 0, 0, 0))
                                        if (to_sq == self.enpassant):
                                            self.add_move(move_list, encode_move(sq, to_sq, 0, 1, 0, 1, 0))
                    if self.board[sq] == K:
                        if (self.castle & castling['K']):
                            if (not self.board[squares['f1']]) and (not self.board[squares['g1']]):
                                if (not self.is_square_attacked(squares['e1'], sides['black'])) and (not self.is_square_attacked(squares['f1'], sides['black'])):
                                    self.add_move(move_list, encode_move(squares['e1'], squares['g1'], 0, 0, 0, 0, 1))
                        if (self.castle & castling['Q']):
                            if (not self.board[squares['d1']]) and (not self.board[squares['b1']]) and (not self.board[squares['c1']]):
                                if (not self.is_square_attacked(squares['e1'], sides['black'])) and (not self.is_square_attacked(squares['d1'], sides['black'])):
                                    self.add_move(move_list, encode_move(squares['e1'], squares['c1'], 0, 0, 0, 0, 1))
                else:
                    if self.board[sq] == p:
                        to_sq = sq + 16
                        if (not (to_sq & 0x88) and (not self.board[to_sq])):
                            if (sq >= squares['a2'] and sq <= squares['h2']):
                                self.add_move(move_list, encode_move(sq, to_sq, q, 0, 0, 0, 0))
                                self.add_move(move_list, encode_move(sq, to_sq, r, 0, 0, 0, 0))
                                self.add_move(move_list, encode_move(sq, to_sq, b, 0, 0, 0, 0))
                                self.add_move(move_list, encode_move(sq, to_sq, n, 0, 0, 0, 0))
                            else:
                                self.add_move(move_list, encode_move(sq, to_sq, 0, 0, 0, 0, 0))
                                if ((sq >= squares['a7'] and sq <= squares['h7']) and (not self.board[sq + 32])):
                                    self.add_move(move_list, encode_move(sq, sq + 32, 0, 0, 1, 0, 0))
                        for i in range(4):
                            pawn_offset = bishop_offsets[i]
                            if (pawn_offset > 0):
                                to_sq = sq + pawn_offset
                                if (not (to_sq & 0x88)):
                                    if (sq >= squares['a2'] and sq <= squares['h2']) and\
                                        (self.board[to_sq] >= 1 and self.board[to_sq] <= 6):
                                        self.add_move(move_list, encode_move(sq, to_sq, q, 1, 0, 0, 0))
                                        self.add_move(move_list, encode_move(sq, to_sq, r, 1, 0, 0, 0))
                                        self.add_move(move_list, encode_move(sq, to_sq, b, 1, 0, 0, 0))
                                        self.add_move(move_list, encode_move(sq, to_sq, n, 1, 0, 0, 0))
                                    else:
                                        if (self.board[to_sq] >= 1 and self.board[to_sq] <= 6):
                                            self.add_move(move_list, encode_move(sq, to_sq, 0, 1, 0, 0, 0))
                                        if (to_sq == self.enpassant):
                                            self.add_move(move_list, encode_move(sq, to_sq, 0, 1, 0, 1, 0))
                    if self.board[sq] == k:
                        if (self.castle & castling['k']):
                            if (not self.board[squares['f8']]) and (not self.board[squares['g8']]):
                                if (not self.is_square_attacked(squares['e8'], sides['white'])) and (not self.is_square_attacked(squares['f8'], sides['white'])):
                                    self.add_move(move_list, encode_move(squares['e8'], squares['g8'], 0, 0, 0, 0, 1))
                        if (self.castle & castling['q']):
                            if (not self.board[squares['d8']]) and (not self.board[squares['b8']]) and (not self.board[squares['c8']]):
                                if (not self.is_square_attacked(squares['e8'], sides['white'])) and (not self.is_square_attacked(squares['d8'], sides['white'])):
                                    self.add_move(move_list, encode_move(squares['e8'], squares['c8'], 0, 0, 0, 0, 1))

                if ((self.board[sq] == N) if self.side else (self.board[sq] == n)):
                    for i in range(8):
                        to_sq = sq + knight_offsets[i]
                        if 0 <= to_sq <= 127:
                            piece = self.board[to_sq]
                            if (not (to_sq & 0x88)):
                                if (not piece or (piece >= 7 and piece <= 12)) if self.side else\
                                    (not piece or (piece >= 1 and piece <= 6)):
                                    if (piece):
                                        self.add_move(move_list, encode_move(sq, to_sq, 0, 1, 0, 0, 0))
                                    else: self.add_move(move_list, encode_move(sq, to_sq, 0, 0, 0, 0, 0))

                if ((self.board[sq] == K) if self.side else (self.board[sq] == k)):
                    for i in range(8):
                        to_sq = sq + king_offsets[i]
                        if 0 <= to_sq <= 127:
                            piece = self.board[to_sq]
                            if (not (to_sq & 0x88)):
                                if (not piece or (piece >= 7 and piece <= 12)) if self.side else\
                                    (not piece or (piece >= 1 and piece <= 6)):
                                    if (piece):
                                        self.add_move(move_list, encode_move(sq, to_sq, 0, 1, 0, 0, 0))
                                    else: self.add_move(move_list, encode_move(sq, to_sq, 0, 0, 0, 0, 0))

                if (((self.board[sq] == B) or (self.board[sq] == Q)) if self.side\
                    else ((self.board[sq] == b) or (self.board[sq] == q))):
                    for i in range(4):
                        to_sq = sq + bishop_offsets[i]
                        while (not (to_sq & 0x88)):
                            if 0 <= to_sq <= 127:
                                piece = self.board[to_sq]
                                if ((1 <= piece <= 6) if self.side else (7 <= piece <= 12)): break
                                if ((7 <= piece <= 12) if self.side else (1 <= piece <= 6)):
                                    self.add_move(move_list, encode_move(sq, to_sq, 0, 1, 0, 0, 0))
                                    break
                                if (not piece): self.add_move(move_list, encode_move(sq, to_sq, 0, 0, 0, 0, 0))
                                to_sq += bishop_offsets[i]


                if (((self.board[sq] == R) or (self.board[sq] == Q)) if self.side\
                    else ((self.board[sq] == r) or (self.board[sq] == q))):
                    for i in range(4):
                        to_sq = sq + rook_offsets[i]
                        while (not (to_sq & 0x88)):
                            if 0 <= to_sq <= 127:
                                piece = self.board[to_sq]
                                if ((1 <= piece <= 6) if self.side else (7 <= piece <= 12)): break
                                if ((7 <= piece <= 12) if self.side else (1 <= piece <= 6)):
                                    self.add_move(move_list, encode_move(sq, to_sq, 0, 1, 0, 0, 0))
                                    break
                                if (not piece): self.add_move(move_list, encode_move(sq, to_sq, 0, 0, 0, 0, 0))
                                to_sq += rook_offsets[i]




    def perft_driver(self, depth:int):
        # break out of recursive state
        if (not depth):
            self.nodes += 1
            return

        # define struct
        move_list = moves_struct()

        # generate moves
        self.gen_moves(move_list)

        # loop over move list
        for mv_count in range(move_list.count):

            # copy board state
            board_cpy = full_cpy(self.board)
            side_cpy = full_cpy(self.side)
            enpassant_cpy = full_cpy(self.enpassant)
            castle_cpy = full_cpy(self.castle)
            king_square_cpy = full_cpy(self.king_square)

            # filter out the illegal moves
            if (not self.make_move(move_list.moves[mv_count], capture_flags['all_moves'])):
                continue

            # recursive call
            self.perft_driver(depth - 1)

            # restore position
            self.board = full_cpy(board_cpy)
            self.side = full_cpy(side_cpy)
            self.enpassant = full_cpy(enpassant_cpy)
            self.castle = full_cpy(castle_cpy)
            self.king_square = full_cpy(king_square_cpy)

    def perft_test(self, depth:int):
        print('\n  [   PERFT TEST   ]\n')

        # init start time
        start_time = perf_counter()

        # define move list
        move_list = moves_struct()

        # generate moves
        self.gen_moves(move_list)

        # loop over move list
        for move_count in range(move_list.count):
            board_cpy = full_cpy(self.board)
            side_cpy = full_cpy(self.side)
            enpassant_cpy = full_cpy(self.enpassant)
            castle_cpy = full_cpy(self.castle)
            king_square_cpy = full_cpy(self.king_square)

            if (not self.make_move(move_list.moves[move_count], capture_flags['all_moves'])):
                continue

            # cummulative NODES
            cum_nodes = self.nodes

            # recursive call
            self.perft_driver(depth - 1)

            # old nodes
            old_nodes = self.nodes - cum_nodes

            # restore board state
            self.board = full_cpy(board_cpy)
            self.side = full_cpy(side_cpy)
            self.enpassant = full_cpy(enpassant_cpy)
            self.castle = full_cpy(castle_cpy)
            self.king_square = full_cpy(king_square_cpy)

            if get_move_piece(move_list.moves[move_count]):
                print('{}{}{}: {}'.format(
                    square_to_coords[get_move_source(move_list.moves[move_count])],
                    square_to_coords[get_move_target(move_list.moves[move_count])],
                    promoted_pieces[get_move_piece(move_list.moves[move_count])],
                    old_nodes
                ))
            else:
                print('{}{}: {}'.format(
                    square_to_coords[get_move_source(move_list.moves[move_count])],
                    square_to_coords[get_move_target(move_list.moves[move_count])],
                    old_nodes
                ))
        print(f'\n  [DEPTH]: {depth}')
        print(f'  [NODES]: {self.nodes}')
        print(f'  [SEARCH TIME]: {convert_to_ms(perf_counter() - start_time)} MS')

    def print_board(self) -> None:
        print()
        print('________________________________\n\n')
        for rank in range(8):
            for file in range(16):
                square = self.conv_rf_idx(rank, file)
                if (file == 0):
                    print('     ', 8 - rank, end='  ')
                if (not (square & 0x88)):
                    print(ascii_pieces[self.board[square]], end=' ')
            print()
        print('\n         a b c d e f g h\n')
        print('________________________________\n')
        print(f'  [SIDE TO MOVE]: {"white" if self.side else "black"} | {self.side}')
        print('  [CURRENT CASTLING RIGHTS]: {}{}{}{} | {}'.format(
                'K' if (self.castle & castling['K']) else '-',
                'Q' if (self.castle & castling['Q']) else '-',
                'k' if (self.castle & castling['k']) else '-',
                'q' if (self.castle & castling['q']) else '-',
                self.castle,
            ))
        if self.enpassant != squares['null_sq']:
            print(f'  [ENPASSANT TARGET SQUARE]: {square_to_coords[self.enpassant]} | {self.enpassant}')
        else: print(f'  [ENPASSANT TARGET SQUARE]: NONE | {self.enpassant}')
        print(f'  [KING SQUARE]: {square_to_coords[self.king_square[self.side]]} | {self.king_square[self.side]}')
        print(f'  [PARSED FEN]: {self.parsed_fen}')

    def print_attack_map(self, side:int):
        print()
        for rank in range(8):
            for file in range(16):
                square = self.conv_rf_idx(rank, file)
                if (file == 0):
                    print(8 - rank, end='  ')
                if (not (square & 0x88)):
                    print('x' if self.is_square_attacked(square, side) else '.', end=' ')
            print()
        print('\n   a b c d e f g h\n')
        print('________________________________\n')
        print(f'[SIDE TO MOVE]: {"white" if self.side else "black"}')
        print(f"[SIDE ATTACKING]: {'white' if side else 'black'}")
        print('[CURRENT CASTLING RIGHTS]: {}{}{}{}'.format(
                'K' if (self.castle & castling['K']) else '-',
                'Q' if (self.castle & castling['Q']) else '-',
                'k' if (self.castle & castling['k']) else '-',
                'q' if (self.castle & castling['q']) else '-',
            ))
        if self.enpassant != squares['null_sq']:
            print(f'[ENPASSANT TARGET SQUARE]: {square_to_coords[self.enpassant]}')
        else: print(f'[ENPASSANT TARGET SQUARE]: NONE')

    def print_board_idx(self): #purely for debugging purposes
        print()
        for rank in range(8):
            for file in range(16):
                square = self.conv_rf_idx(rank, file)
                print(square, end=' ')
            print()

    def print_board_fancy(self):
        print()
        for rank in range(8):
            for file in range(16):
                square = self.conv_rf_idx(rank, file)
                if (file == 0):
                    print(8 - rank, end='  ')
                if (not (square & 0x88)):
                    print(unicode_pieces[self.board[square]], end=' ')
            print()
        print('\n   a b c d e f g h\n')
        print('________________________________\n')
        print(f'[SIDE TO MOVE]: {"white" if self.side else "black"}')
        print('[CURRENT CASTLING RIGHTS]: {}{}{}{}'.format(
                'K' if (self.castle & castling['K']) else '-',
                'Q' if (self.castle & castling['Q']) else '-',
                'k' if (self.castle & castling['k']) else '-',
                'q' if (self.castle & castling['q']) else '-',
            ))
        if self.enpassant != squares['null_sq']:
            print(f'[ENPASSANT TARGET SQUARE]: {square_to_coords[self.enpassant]}')
        else: print(f'[ENPASSANT TARGET SQUARE]: NONE')
        print(f'[PARSED FEN]: {self.parsed_fen}')

def print_move_list(move_list:moves_struct, mode:str) -> None:
    if mode == 'full':
        print('\nMOVE   CAPTURE   DOUBLE   ENPASS   CASTLING\n')
    else: print()
    for idx in range(move_list.count):
        move = move_list.moves[idx]
        if move == None: continue
        formated_move = '{}{}'.format(square_to_coords[get_move_source(move)], square_to_coords[get_move_target(move)])
        promotion_move = promoted_pieces[get_move_piece(move)] if (get_move_piece(move)) else ' '
        joined_str = '{}{}'.format(formated_move, promotion_move)
        if mode == 'full':
            print('{}  {}         {}        {}        {}'.format(
                        joined_str,
                        get_move_capture(move),
                        get_move_pawn(move),
                        get_move_enpassant(move),
                        get_move_castling(move))),
        elif mode == 'raw':
            print(joined_str)

    print(f'\n  [TOTAL MOVES: {move_list.count}, TEMPEST_001]')

import sys

if (__name__ == '__main__'):

    # init and print stuff because yes
    print('\n[WELCOME TO TEMPEST CHESS ENGINE v2.1]')
    print(f'[RUNNING ON]: {sys.version}')

    # init board and parse FEN
    bboard = board()
    bboard.timer.init_time()
    bboard.parse_fen(start_position)
    bboard.print_board()

    bboard.perft_test(5)

    bboard.timer.mark_time()

    print(f'\n  [PROGRAM FINISHED IN {round(bboard.timer.program_runtime * 1000)} MS, {bboard.timer.program_runtime} SEC]')
