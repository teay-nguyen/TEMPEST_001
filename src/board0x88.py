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
from time import perf_counter
from uuid import uuid4
from defs import *

# state variables
a8 =   0;    b8 = 1;    c8 = 2;   d8 = 3;    e8 = 4;   f8 = 5;   g8 = 6;   h8 = 7;
a7 =  16;   b7 = 17;   c7 = 18;  d7 = 19;   e7 = 20;  f7 = 21;  g7 = 22;  h7 = 23;
a6 =  32;   b6 = 33;   c6 = 34;  d6 = 35;   e6 = 36;  f6 = 37;  g6 = 39;  h6 = 40;
a5 =  48;   b5 = 49;   c5 = 50;  d5 = 51;   e5 = 52;  f5 = 53;  g5 = 54;  h5 = 55;
a4 =  64;   b4 = 65;   c4 = 66;  d4 = 67;   e4 = 68;  f4 = 69;  g4 = 70;  h4 = 71;
a3 =  80;   b3 = 81;   c3 = 82;  d3 = 83;   e3 = 84;  f3 = 85;  g3 = 86;  h3 = 87;
a2 =  96;   b2 = 97;   c2 = 98;  d2 = 99;  e2 = 100; f2 = 101; g2 = 102; h2 = 103;
a1 = 112;  b1 = 113;  c1 = 114; d1 = 115;  e1 = 116; f1 = 117; g1 = 118; h1 = 119;   offboard = 120

offboard_mask:int = 0x88

'''

    NOTE: Found UUID module to be faster, this is unused for now
    NOTE: Algorithm taken from Stockfish Chess Engine, translated into Python

    RKISS is TEMPEST_001's (secondary) pseudo random number generator (PRNG) used to compute hash keys.
    George Marsaglia invented the RNG-Kiss-family in the early 90's. This is a
    specific version that Heinz van Saanen derived from some public domain code
    by Bob Jenkins. Following the feature list, as tested by Heinz.

    - Quite platform independent
    - ~4 times faster than SSE2-version of Mersenne twister
    - Average cycle length: ~2^126
    - 64 bit seed
    - Return doubles with a full 53 bit mantissa
    - Thread safe (if Python removes the GIL that is)

'''

# RKISS class
class RKISS:
    def __init__(self):
        self.a:int = 0; self.b:int = 0; self.c:int = 0; self.d:int = 0

        # call init to calculate random unsigned 64 bit numbers
        self.raninit()

    def rotate(self, x:int, k:int) -> int:
        return (x << k) | (x >> (64 - k))

    def raninit(self) -> None:
        self.a = 0xf1ea5eed
        self.b = self.c = self.d = 0xd4e12c77
        for _ in range(20): self.rand64()

    def rand64(self) -> int:
        e = self.a - self.rotate(self.b, 7)
        self.a = self.b ^ self.rotate(self.c, 13)
        self.b = self.c + self.rotate(self.d, 37)
        self.c = self.d + e
        self.d = e + self.a
        return self.d

'''
    Method of generating random keys by BBC (BitBoard Chess) by CMK

    - Given a random seed, the algorithm turns it into a random 32 bit number
    - Does some magic bit manipulation and a random 64 bit number pops out
'''

class CMK_Rand:
    def __init__(self):
        self.seed = 1804289383

    def rand32(self):
        number:int = self.seed
        number ^= number << 13
        number ^= number >> 17
        number ^= number << 5
        self.seed = number
        return number

    def rand64(self):
        n1:int = self.rand32() & 0xFFFF
        n2:int = self.rand32() & 0xFFFF
        n3:int = self.rand32() & 0xFFFF
        n4:int = self.rand32() & 0xFFFF
        return n1 | (n2 << 16) | (n3 << 32) | (n4 << 48)

class Zobrist:
    def __init__(self) -> None:
        self.secondary_generator = CMK_Rand()
        self.rand64 = self.secondary_generator.rand64
        self.piecesquare: list = [[self.rand64() for _ in range(BSQUARES)] for _ in range(PIECE_TYPES)]
        self.side: int = self.rand64()
        self.castling: list = [self.rand64() for _ in range(CASTLE_VAL)]
        self.ep: list = [self.rand64() for _ in range(BSQUARES)]

class Zobrist_v2:
    def __init__(self) -> None:
        self.piecesquare: list = [[self.rand64() for _ in range(BSQUARES)] for _ in range(PIECE_TYPES)]
        self.side: int = self.rand64()
        self.castling: list = [self.rand64() for _ in range(CASTLE_VAL)]
        self.ep: list = [self.rand64() for _ in range(BSQUARES)]

    def rand64(self): return uuid4().int >> 64

class MovesStruct:
    def __init__(self) -> None:
        self.moves:list = [move_t() for _ in range(GEN_STACK)]
        self.count:int = 0

class BoardState:
    def __init__(self) -> None:
        self.zobrist: Zobrist_v2 = Zobrist_v2()
        self.fifty: int = 0
        self.hash_key: int = 0
        self.nodes: int = 0
        self.parsed_fen: str = ''
        self.king_square: list = [e8, e1]
        self.side: int = -1
        self.xside: int = -1
        self.castle: int = 0
        self.enpassant: int = offboard
        self.pce_pos: list = [[0 for _ in range(MAX_PCE_EACH_TYPE)] for _ in range(PIECE_TYPES)]
        self.pce_count: list = [0 for _ in range(PIECE_TYPES)]
        self.reps: list = []
        self.board: list = [
            r, n, b, q, k, b, n, r,  o, o, o, o, o, o, o, o,
            p, p, p, p, p, p, p, p,  o, o, o, o, o, o, o, o,
            e, e, e, e, e, e, e, e,  o, o, o, o, o, o, o, o,
            e, e, e, e, e, e, e, e,  o, o, o, o, o, o, o, o,
            e, e, e, e, e, e, e, e,  o, o, o, o, o, o, o, o,
            e, e, e, e, e, e, e, e,  o, o, o, o, o, o, o, o,
            P, P, P, P, P, P, P, P,  o, o, o, o, o, o, o, o,
            R, N, B, Q, K, B, N, R,  o, o, o, o, o, o, o, o,
        ]

    def gen_hashkey(self) -> None:
        self.hash_key = 0
        for sq in range(len(self.board)):
            if not (sq & offboard_mask):
                piece:int = self.board[sq]
                if piece: self.hash_key ^= self.zobrist.piecesquare[piece][sq]
        if self.enpassant != offboard: self.hash_key ^= self.zobrist.ep[self.enpassant]
        self.hash_key ^= self.zobrist.castling[self.castle]
        if not self.side: self.hash_key ^= self.zobrist.side

    def init_state(self, fen:str) -> None:
        self.clear_board()
        self.parse_fen(fen)
        self.gen_hashkey()

    def clear_board(self) -> None:
        # sweep the surface clean
        for rank in range(MAX_RANKS):
            for file in range(MAX_FILES):
                square:int = rank * MAX_FILES + file
                if not (square & offboard_mask):
                    self.board[square] = e

        self.fifty: int = 0
        self.pce_pos: list = [[0 for _ in range(MAX_PCE_EACH_TYPE)] for _ in range(PIECE_TYPES)]
        self.pce_count: list = [0 for _ in range(PIECE_TYPES)]
        self.hash_key: int = 0
        self.nodes: int = 0
        self.parsed_fen: str = ''
        self.king_square: list = [e8, e1]
        self.side: int = -1
        self.xside: int = -1
        self.castle: int = 0
        self.enpassant: int = offboard
        self.reps: list = []

    def generate_fen(self) -> str:
        fen_string: str = ''
        empty: int = 0

        # filling up the string with pieces
        for r in range(MAX_RANKS):
            for f in range(MAX_FILES):
                sq = r * MAX_FILES + f
                if not (sq & offboard_mask):
                    if self.board[sq] == e: empty += 1
                    elif P <= self.board[sq] <= k:
                        if empty: fen_string = f'{fen_string}{empty}'; empty = 0
                        fen_string = f'{fen_string}{int_pieces[self.board[sq]]}'
            if empty: fen_string = f'{fen_string}{empty}'; empty = 0
            fen_string = f'{fen_string}/'
        fen_string = fen_string[:-1]
        if self.side: fen_string = f'{fen_string} w '
        else: fen_string = f'{fen_string} b '
        return fen_string

    def parse_fen(self, fen:str) -> None:
        # clear board before parsing string
        self.clear_board()

        # load pieces onto board
        self.parsed_fen = fen
        fen_segments:list = fen.split()
        rank:int = 0
        file:int = 0

        for sym in fen_segments[0]:
            if sym == '/':
                file = 0
                rank += 1
            else:
                if sym.isdigit():
                    assert int(sym) >= 0 and int(sym) <= 9
                    file += int(sym)
                else:
                    assert (ord('a') <= ord(sym) <= ord('z')) or (ord('A') <= ord(sym) <= ord('Z')) # unorthodoxed method to check FEN string but it works
                    square:int = rank * MAX_FILES + file
                    if not (square & offboard_mask):
                        if P <= char_pieces[sym] <= k:
                            self.pce_pos[char_pieces[sym]][self.pce_count[char_pieces[sym]]] = square
                            self.pce_count[char_pieces[sym]] += 1
                            if sym == 'K': self.king_square[sides['white']] = square
                            elif sym == 'k': self.king_square[sides['black']] = square
                            self.board[square] = char_pieces[sym]
                        file += 1

        # choose which side goes first
        side_segment:str = fen_segments[1]
        if side_segment == 'w':
            self.side = sides['white']
            self.xside = sides['black']
        elif side_segment == 'b':
            self.side = sides['black']
            self.xside = sides['white']
        else: self.side = -1; self.xside = -1

        # castle rights parsing
        castling_segment:str = fen_segments[2]
        if castling_segment != '-':
            for sym in castling_segment:
                if sym == 'K': self.castle |= castling_vals['K']
                elif sym == 'Q': self.castle |= castling_vals['Q']
                elif sym == 'k': self.castle |= castling_vals['k']
                elif sym == 'q': self.castle |= castling_vals['q']

        # load enpassant square
        fen_ep:str = fen_segments[3]
        if fen_ep != '-':
            file:int = ord(fen_ep[0]) - ord('a')
            rank:int = 8 - (ord(fen_ep[1]) - ord('0'))
            self.enpassant = rank * MAX_FILES + file
        else: self.enpassant = offboard


    def in_check(self, side:int) -> int:
        return self.sq_attacked_optimized(self.king_square[side], side ^ 1)

    def is_square_attacked(self, square:int, oppside:int) -> int:
        # pawn attacks
        if oppside:
            if not (square + 17) & offboard_mask and self.board[square + 17] == P: return 1
            if not (square + 15) & offboard_mask and self.board[square + 15] == P: return 1
        else:
            if not (square - 17) & offboard_mask and self.board[square - 17] == p: return 1
            if not (square - 15) & offboard_mask and self.board[square - 15] == p: return 1

        # knight attacks
        for i in range(8):
            target_sq:int = square + knight_offsets[i]
            if not (target_sq & offboard_mask):
                target_piece:int = self.board[target_sq]
                if (target_piece == N) if oppside else (target_piece == n): return 1

        # king attacks
        for i in range(8):
            target_sq:int = square + king_offsets[i]
            if not (target_sq & offboard_mask):
                target_piece:int = self.board[target_sq]
                if (target_piece == K) if oppside else (target_piece == k): return 1

        # bishop attacks
        for i in range(4):
            target_sq:int = square + bishop_offsets[i]
            while not (target_sq & offboard_mask):
                target_piece:int = self.board[target_sq]
                if (target_piece == B or target_piece == Q) if oppside else (target_piece == b or target_piece == q): return 1
                if target_piece: break
                target_sq += bishop_offsets[i]

        # rook attacks
        for i in range(4):
            target_sq:int = square + rook_offsets[i]
            while not (target_sq & offboard_mask):
                target_piece:int = self.board[target_sq]
                if (target_piece == R or target_piece == Q) if oppside else (target_piece == r or target_piece == q): return 1
                if target_piece: break
                target_sq += rook_offsets[i]
        return 0

    def sq_attacked_optimized(self, sq:int, oppside:int) -> int:
        if oppside:
            if not (sq + 17) & offboard_mask and self.board[sq + 17] == P: return 1
            if not (sq + 15) & offboard_mask and self.board[sq + 15] == P: return 1
        else:
            if not (sq - 17) & offboard_mask and self.board[sq - 17] == p: return 1
            if not (sq - 15) & offboard_mask and self.board[sq - 15] == p: return 1

        for _i in range(4):
            target_sq:int = sq; step:int = 0
            while 1:
                target_sq += bishop_offsets[_i]; step += 1
                if target_sq & offboard_mask: break
                target_piece:int = self.board[target_sq]
                if not target_piece: continue
                if (target_piece == B or target_piece == Q) if oppside else (target_piece == b or target_piece == q): return 1
                if step == 1 and ((target_piece == K) if oppside else (target_piece == k)): return 1
                break

        for _i in range(4):
            target_sq:int = sq; step:int = 0
            while 1:
                target_sq += rook_offsets[_i]; step += 1
                if target_sq & offboard_mask: break
                target_piece:int = self.board[target_sq]
                if not target_piece: continue
                if (target_piece == R or target_piece == Q) if oppside else (target_piece == r or target_piece == q): return 1
                if step == 1 and ((target_piece == K) if oppside else (target_piece == k)): return 1
                break

        for i in range(8):
            target_sq:int = sq + knight_offsets[i]
            if not (target_sq & offboard_mask):
                target_piece:int = self.board[target_sq]
                if (target_piece == N) if oppside else (target_piece == n): return 1
        return 0

    def make_move(self, move:int, capture_flag:int, searching:int = 0) -> int: # bound to return a int, in replacement for bool

        # filter out the None moves
        if move == -1: return 0 # illegal anyway because this is not a valid move on the board

        # quiet moves
        if capture_flag == ALL_MOVES:
            # copy stuff
            board_cpy:list = [_ for _ in self.board]
            side_cpy:int = self.side
            xside_cpy:int = self.xside
            enpassant_cpy:int = self.enpassant
            castle_cpy:int = self.castle
            king_square_cpy:list = [_ for _ in self.king_square]
            pce_count_cpy:list = [_ for _ in self.pce_count]
            hashkey_cpy:int = self.hash_key
            fifty_cpy:int = self.fifty
            reps_cpy:list = [_ for _ in self.reps]

            # get move source and the square it moves to
            from_square:int = get_move_source(move)
            to_square:int = get_move_target(move)
            promoted_piece:int = get_move_promoted(move)
            enpass:int = get_move_enpassant(move)
            double_push:int = get_move_pawn(move)
            castling:int = get_move_castling(move)

            # perform the move
            captured_piece:int = self.board[to_square]
            piece_moved:int = self.board[from_square]
            self.board[to_square] = self.board[from_square]
            self.board[from_square] = e
            self.hash_key ^= self.zobrist.piecesquare[piece_moved][from_square]
            self.hash_key ^= self.zobrist.piecesquare[piece_moved][to_square]

            self.fifty += 1

            # adjusting board state
            if captured_piece:
                self.hash_key ^= self.zobrist.piecesquare[captured_piece][to_square]
                self.pce_count[captured_piece] -= 1
                self.fifty = 0
            elif self.board[to_square] == P or self.board[to_square] == p: self.fifty = 0
            if promoted_piece:
                self.pce_count[self.board[to_square]] -= 1
                self.board[to_square] = promoted_piece
                self.pce_count[promoted_piece] += 1
                if self.side: self.hash_key ^= self.zobrist.piecesquare[P][to_square]
                else: self.hash_key ^= self.zobrist.piecesquare[p][to_square]
                self.hash_key ^= self.zobrist.piecesquare[promoted_piece][to_square]
            if enpass:
                self.pce_count[self.board[to_square + 16 if self.side else to_square - 16]] -= 1
                self.board[to_square + 16 if self.side else to_square - 16] = e
                if self.side: self.hash_key ^= self.zobrist.piecesquare[p][to_square + 16]
                else: self.hash_key ^= self.zobrist.piecesquare[P][to_square - 16]
            if self.enpassant != offboard: self.hash_key ^= self.zobrist.ep[self.enpassant]
            self.enpassant = offboard
            if double_push:
                self.enpassant = to_square + 16 if self.side else to_square - 16
                if self.side: self.hash_key ^= self.zobrist.ep[to_square + 16]
                else: self.hash_key ^= self.zobrist.ep[to_square - 16]
            if castling:
                if to_square == g1:
                    self.board[f1] = self.board[h1]
                    self.board[h1] = e
                    self.hash_key ^= self.zobrist.piecesquare[R][h1]
                    self.hash_key ^= self.zobrist.piecesquare[R][f1]
                elif to_square == c1:
                    self.board[d1] = self.board[a1]
                    self.board[a1] = e
                    self.hash_key ^= self.zobrist.piecesquare[R][a1]
                    self.hash_key ^= self.zobrist.piecesquare[R][d1]
                elif to_square == g8:
                    self.board[f8] = self.board[h8]
                    self.board[h8] = e
                    self.hash_key ^= self.zobrist.piecesquare[r][h8]
                    self.hash_key ^= self.zobrist.piecesquare[r][f8]
                elif to_square == c8:
                    self.board[d8] = self.board[a8]
                    self.board[a8] = e
                    self.hash_key ^= self.zobrist.piecesquare[r][a8]
                    self.hash_key ^= self.zobrist.piecesquare[r][d8]

            # update king square
            if self.board[to_square] == K or self.board[to_square] == k: self.king_square[self.side] = to_square

            # update castling rights
            self.hash_key ^= self.zobrist.castling[self.castle]
            self.castle &= castling_rights[from_square]
            self.castle &= castling_rights[to_square]
            self.hash_key ^= self.zobrist.castling[self.castle]

            # change sides
            self.side ^= 1
            self.xside ^= 1
            self.hash_key ^= self.zobrist.side

            # update repetition table
            if not searching:
                if piece_moved == P or piece_moved == p or captured_piece: self.reps:list = []; self.fifty = 0
                else: self.reps.append(self.hash_key)

            # take back move if king is under attack
            if self.in_check(self.xside):
                self.board = [_ for _ in board_cpy]
                self.side = side_cpy
                self.xside = xside_cpy
                self.enpassant = enpassant_cpy
                self.castle = castle_cpy
                self.king_square = [_ for _ in king_square_cpy]
                self.pce_count = [_ for _ in pce_count_cpy]
                self.hash_key = hashkey_cpy
                self.fifty = fifty_cpy
                self.reps = [_ for _ in reps_cpy]
                return 0 # illegal
            else: return 1 # legal
        elif capture_flag == CAPTURE_MOVES:
            if get_move_capture(move): self.make_move(move, ALL_MOVES, searching=searching)
            else: return 0 # move is not a capture
        return 0 # returns 0 if flag is not equal to either set flags

    def add_move(self, move_list: MovesStruct, move: int) -> None:
        move_list.moves[move_list.count].move = move
        move_list.count += 1

    def gen_moves(self, move_list: MovesStruct) -> None:
        move_list.count = 0
        for sq in range(BSQUARES):
            if not (sq & offboard_mask):
                if self.side:
                    if self.board[sq] == P:
                        to_sq:int = sq - 16
                        if not (to_sq & offboard_mask) and not self.board[to_sq]:
                            if a7 <= sq <= h7:
                                self.add_move(move_list, encode_move(sq, to_sq, Q, 0, 0, 0, 0))
                                self.add_move(move_list, encode_move(sq, to_sq, R, 0, 0, 0, 0))
                                self.add_move(move_list, encode_move(sq, to_sq, B, 0, 0, 0, 0))
                                self.add_move(move_list, encode_move(sq, to_sq, N, 0, 0, 0, 0))
                            else:
                                self.add_move(move_list, encode_move(sq, to_sq, 0, 0, 0, 0, 0))
                                if sq >= a2 and sq <= h2 and not self.board[sq - 32]: self.add_move(move_list, encode_move(sq, sq - 32, 0, 0, 1, 0, 0))
                        for i in range(2):
                            pawn_offset:int = bishop_offsets[i+2]
                            to_sq:int = sq + pawn_offset
                            if not (to_sq & offboard_mask):
                                if (sq >= a7 and sq <= h7) and\
                                    (self.board[to_sq] >= 7 and self.board[to_sq] <= 12):
                                    self.add_move(move_list, encode_move(sq, to_sq, Q, 1, 0, 0, 0))
                                    self.add_move(move_list, encode_move(sq, to_sq, R, 1, 0, 0, 0))
                                    self.add_move(move_list, encode_move(sq, to_sq, B, 1, 0, 0, 0))
                                    self.add_move(move_list, encode_move(sq, to_sq, N, 1, 0, 0, 0))
                                else:
                                    if self.board[to_sq] >= 7 and self.board[to_sq] <= 12: self.add_move(move_list, encode_move(sq, to_sq, 0, 1, 0, 0, 0))
                                    if to_sq == self.enpassant: self.add_move(move_list, encode_move(sq, to_sq, 0, 1, 0, 1, 0))
                    if self.board[sq] == K:
                        if self.castle & castling_vals['K']:
                            if not self.board[f1] and not self.board[g1]:
                                if not self.sq_attacked_optimized(e1, sides['black']) and not self.sq_attacked_optimized(f1, sides['black']):
                                    self.add_move(move_list, encode_move(e1, g1, 0, 0, 0, 0, 1))
                        if self.castle & castling_vals['Q']:
                            if not self.board[d1] and not self.board[b1] and not self.board[c1]:
                                if not self.sq_attacked_optimized(e1, sides['black']) and not self.sq_attacked_optimized(d1, sides['black']):
                                    self.add_move(move_list, encode_move(e1, c1, 0, 0, 0, 0, 1))
                else:
                    if self.board[sq] == p:
                        to_sq:int = sq + 16
                        if not (to_sq & offboard_mask) and not self.board[to_sq]:
                            if sq >= a2 and sq <= h2:
                                self.add_move(move_list, encode_move(sq, to_sq, q, 0, 0, 0, 0))
                                self.add_move(move_list, encode_move(sq, to_sq, r, 0, 0, 0, 0))
                                self.add_move(move_list, encode_move(sq, to_sq, b, 0, 0, 0, 0))
                                self.add_move(move_list, encode_move(sq, to_sq, n, 0, 0, 0, 0))
                            else:
                                self.add_move(move_list, encode_move(sq, to_sq, 0, 0, 0, 0, 0))
                                if sq >= a7 and sq <= h7 and not self.board[sq + 32]:
                                    self.add_move(move_list, encode_move(sq, sq + 32, 0, 0, 1, 0, 0))
                        for i in range(2):
                            pawn_offset:int = bishop_offsets[i]
                            to_sq = sq + pawn_offset
                            if not (to_sq & offboard_mask):
                                if (sq >= a2 and sq <= h2) and\
                                    (self.board[to_sq] >= 1 and self.board[to_sq] <= 6):
                                    self.add_move(move_list, encode_move(sq, to_sq, q, 1, 0, 0, 0))
                                    self.add_move(move_list, encode_move(sq, to_sq, r, 1, 0, 0, 0))
                                    self.add_move(move_list, encode_move(sq, to_sq, b, 1, 0, 0, 0))
                                    self.add_move(move_list, encode_move(sq, to_sq, n, 1, 0, 0, 0))
                                else:
                                    if self.board[to_sq] >= 1 and self.board[to_sq] <= 6: self.add_move(move_list, encode_move(sq, to_sq, 0, 1, 0, 0, 0))
                                    if to_sq == self.enpassant: self.add_move(move_list, encode_move(sq, to_sq, 0, 1, 0, 1, 0))
                    if self.board[sq] == k:
                        if self.castle & castling_vals['k']:
                            if not self.board[f8] and not self.board[g8]:
                                if not self.sq_attacked_optimized(e8, sides['white']) and not self.sq_attacked_optimized(f8, sides['white']):
                                    self.add_move(move_list, encode_move(e8, g8, 0, 0, 0, 0, 1))
                        if self.castle & castling_vals['q']:
                            if not self.board[d8] and not self.board[b8] and not self.board[c8]:
                                if not self.sq_attacked_optimized(e8, sides['white']) and not self.sq_attacked_optimized(d8, sides['white']):
                                    self.add_move(move_list, encode_move(e8, c8, 0, 0, 0, 0, 1))

                if (self.board[sq] == N) if self.side else (self.board[sq] == n):
                    for i in range(8):
                        to_sq:int = sq + knight_offsets[i]
                        if not (to_sq & offboard_mask):
                            piece:int = self.board[to_sq]
                            if (not piece or (piece >= 7 and piece <= 12)) if self.side else\
                                (not piece or (piece >= 1 and piece <= 6)):
                                if piece: self.add_move(move_list, encode_move(sq, to_sq, 0, 1, 0, 0, 0))
                                else: self.add_move(move_list, encode_move(sq, to_sq, 0, 0, 0, 0, 0))

                if (self.board[sq] == K) if self.side else (self.board[sq] == k):
                    for i in range(8):
                        to_sq:int = sq + king_offsets[i]
                        if not (to_sq & offboard_mask):
                            piece:int = self.board[to_sq]
                            if (not piece or (piece >= 7 and piece <= 12)) if self.side else\
                                (not piece or (piece >= 1 and piece <= 6)):
                                if piece: self.add_move(move_list, encode_move(sq, to_sq, 0, 1, 0, 0, 0))
                                else: self.add_move(move_list, encode_move(sq, to_sq, 0, 0, 0, 0, 0))

                if ((self.board[sq] == B) or (self.board[sq] == Q)) if self.side\
                    else ((self.board[sq] == b) or (self.board[sq] == q)):
                    for i in range(4):
                        to_sq:int = sq + bishop_offsets[i]
                        while not (to_sq & offboard_mask):
                            piece:int = self.board[to_sq]
                            if (1 <= piece <= 6) if self.side else (7 <= piece <= 12): break
                            if (7 <= piece <= 12) if self.side else (1 <= piece <= 6):
                                self.add_move(move_list, encode_move(sq, to_sq, 0, 1, 0, 0, 0))
                                break
                            if not piece: self.add_move(move_list, encode_move(sq, to_sq, 0, 0, 0, 0, 0))
                            to_sq += bishop_offsets[i]


                if ((self.board[sq] == R) or (self.board[sq] == Q)) if self.side\
                    else ((self.board[sq] == r) or (self.board[sq] == q)):
                    for i in range(4):
                        to_sq:int = sq + rook_offsets[i]
                        while not (to_sq & offboard_mask):
                            piece:int = self.board[to_sq]
                            if (1 <= piece <= 6) if self.side else (7 <= piece <= 12): break
                            if (7 <= piece <= 12) if self.side else (1 <= piece <= 6):
                                self.add_move(move_list, encode_move(sq, to_sq, 0, 1, 0, 0, 0))
                                break
                            if not piece: self.add_move(move_list, encode_move(sq, to_sq, 0, 0, 0, 0, 0))
                            to_sq += rook_offsets[i]


    def perft_driver(self, depth:int) -> None:
        # break out of recursive state
        if depth <= 0:
            self.nodes += 1
            return

        # define struct
        move_list: MovesStruct = MovesStruct()

        # generate moves
        self.gen_moves(move_list)

        # loop over move list
        for mv_count in range(move_list.count):

            # copy board state
            board_cpy:list = [_ for _ in self.board]
            side_cpy:int = self.side
            xside_cpy:int = self.xside
            enpassant_cpy:int = self.enpassant
            castle_cpy:int = self.castle
            king_square_cpy:list = [_ for _ in self.king_square]
            pce_count_cpy:list = [_ for _ in self.pce_count]
            hashkey_cpy:int = self.hash_key
            fifty_cpy:int = self.fifty
            reps_cpy:list = [_ for _ in self.reps]

            # filter out the illegal moves
            if not self.make_move(move_list.moves[mv_count].move, ALL_MOVES): continue

            # recursive call
            self.perft_driver(depth - 1)

            # restore position
            self.board = [_ for _ in board_cpy]
            self.side = side_cpy
            self.xside = xside_cpy
            self.enpassant = enpassant_cpy
            self.castle = castle_cpy
            self.king_square = [_ for _ in king_square_cpy]
            self.pce_count = [_ for _ in pce_count_cpy]
            self.hash_key = hashkey_cpy
            self.fifty = fifty_cpy
            self.reps = [_ for _ in reps_cpy]

    def perft_test(self, depth:int = 1) -> None:
        print('\n  [PERFT TEST GENERATING MOVES]\n')

        # define move list
        move_list: MovesStruct = MovesStruct()

        # generate moves
        self.gen_moves(move_list)

        # init start time
        start_time:float = perf_counter()

        # loop over move list
        for mv_count in range(move_list.count):
            board_cpy:list = [_ for _ in self.board]
            side_cpy:int = self.side
            xside_cpy:int = self.xside
            enpassant_cpy:int = self.enpassant
            castle_cpy:int = self.castle
            king_square_cpy:list = [_ for _ in self.king_square]
            pce_count_cpy:list = [_ for _ in self.pce_count]
            hashkey_cpy:int = self.hash_key
            fifty_cpy:int = self.fifty
            reps_cpy:list = [_ for _ in self.reps]

            if not self.make_move(move_list.moves[mv_count].move, ALL_MOVES): continue

            # leaf NODES
            leaf_nodes:int = self.nodes

            # recursive call
            self.perft_driver(depth - 1)

            # old nodes
            old_nodes:int = self.nodes - leaf_nodes

            # restore board state
            self.board = [_ for _ in board_cpy]
            self.side = side_cpy
            self.xside = xside_cpy
            self.enpassant = enpassant_cpy
            self.castle = castle_cpy
            self.king_square = [_ for _ in king_square_cpy]
            self.pce_count = [_ for _ in pce_count_cpy]
            self.hash_key = hashkey_cpy
            self.fifty = fifty_cpy
            self.reps = [_ for _ in reps_cpy]

            if get_move_promoted(move_list.moves[mv_count].move): print(f'  {square_to_coords[get_move_source(move_list.moves[mv_count].move)]}{square_to_coords[get_move_target(move_list.moves[mv_count].move)]}{promoted_pieces[get_move_promoted(move_list.moves[mv_count].move)]}: {old_nodes}')
            else: print(f'  {square_to_coords[get_move_source(move_list.moves[mv_count].move)]}{square_to_coords[get_move_target(move_list.moves[mv_count].move)]}: {old_nodes}')

        elapsed:float = perf_counter() - start_time
        print(f'\n  [SEARCH TIME]: {round(elapsed * 1000)} ms')
        print(f'  [DEPTH SEARCHED]: {depth} ply')
        print(f'  [TOTAL NODES]: {self.nodes} nodes')
        print(f'  [NPS]: {int(self.nodes//elapsed)} nps\n')

    def print_board(self) -> None:
        print('\n----------------------------------\n')
        for rank in range(MAX_RANKS):
            for file in range(MAX_FILES):
                square:int = rank * MAX_FILES + file
                if not file: print('     ', 8 - rank, end='  ')
                if not (square & offboard_mask): print(ascii_pieces[self.board[square]], end=' ')
            print('', end='\n')
        print('\n         a b c d e f g h\n')
        print('----------------------------------\n')
        print(f'  [SIDE TO MOVE]: {"white" if self.side else "black"} | {self.side}')
        print('  [CURRENT CASTLING RIGHTS]: {}{}{}{} | {}'.format(
                'K' if (self.castle & castling_vals['K']) else '-',
                'Q' if (self.castle & castling_vals['Q']) else '-',
                'k' if (self.castle & castling_vals['k']) else '-',
                'q' if (self.castle & castling_vals['q']) else '-',
                self.castle,
            ))
        if self.enpassant != offboard: print(f'  [ENPASSANT TARGET SQUARE]: {square_to_coords[self.enpassant]} | {self.enpassant}')
        else: print(f'  [ENPASSANT TARGET SQUARE]: NONE | {self.enpassant}')
        print(f'  [KING SQUARE]: {square_to_coords[self.king_square[self.side]]} | {self.king_square[self.side]}')
        print(f'  [PIECE LIST]: {self.pce_pos}')
        print(f'  [PIECE COUNT]: {self.pce_count}')
        print(f'  [POSITION KEY]: {self.hash_key}')
        print(f'  [REPETITION HISTORY]: {self.reps}')
        print(f'  [PARSED FEN]: {self.parsed_fen}')

def print_move_list(move_list, mode:str):
    if mode == 'full':
        print('\nMOVE   CAPTURE   DOUBLE   ENPASS   CASTLING\n')
    else: print()
    for idx in range(move_list.count):
        move:int = move_list.moves[idx].move
        if move is None: continue
        formated_move:str = f'{square_to_coords[get_move_source(move)]}{square_to_coords[get_move_target(move)]}'
        promotion_move:str = promoted_pieces[get_move_promoted(move)] if get_move_promoted(move) else ' '
        joined_str:str = f'{formated_move}{promotion_move}'
        if mode == 'full':
            print('{}  {}         {}        {}        {}'.format(
                        joined_str,
                        get_move_capture(move),
                        get_move_pawn(move),
                        get_move_enpassant(move),
                        get_move_castling(move))),
        elif mode == 'raw': print(joined_str)

    print(f'\n  [TOTAL MOVES: {move_list.count}, TEMPEST_001]')
