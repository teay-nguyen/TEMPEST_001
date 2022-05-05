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

#!/usr/bin/env pypy3 -u
# -*- coding: utf-8 -*-

# imports
from time import perf_counter
from uuid import uuid1
from defs import *

'''

    Found UUID module to be faster, this is unused for now

    RKISS is TEMPEST_001's (secondary) pseudo random number generator (PRNG) used to compute hash keys.
    George Marsaglia invented the RNG-Kiss-family in the early 90's. This is a
    specific version that Heinz van Saanen derived from some public domain code
    by Bob Jenkins. Following the feature list, as tested by Heinz.

    - Quite platform independent
    - Passes ALL dieharder tests! Here *nix sys-rand() e.g. fails miserably :-)
    - ~12 times faster than my *nix sys-rand()
    - ~4 times faster than SSE2-version of Mersenne twister
    - Average cycle length: ~2^126
    - 64 bit seed
    - Return doubles with a full 53 bit mantissa
    - Thread safe

'''

class RKISS:
    def __init__(self):
        self.a:int = 0; self.b:int = 0; self.c:int = 0; self.d:int = 0

        # call init to calculate random unsigned 64 bit numbers
        self.raninit()

    def rotate(self, x:int, k:int):
        return (x << k) | (x >> (64 - k))

    def raninit(self):
        self.a = 0xf1ea5eed
        self.b = self.c = self.d = 0xd4e12c77
        for _ in range(73):
            self.rand64()

    def rand64(self):
        e = self.a - self.rotate(self.b, 7)
        self.a = self.b ^ self.rotate(self.c, 13)
        self.b = self.c + self.rotate(self.d, 37)
        self.c = self.d + e
        self.d = e + self.a
        return self.d

class Zobrist:
    def __init__(self) -> None:
        # self.rk:RKISS = RKISS()
        self.piecesquare: list = [[self.rand64() for _ in range(BOARD_SQ_NUM)] for _ in range(PIECE_TYPES)]
        self.side: int = self.rand64()
        self.castling: list = [self.rand64() for _ in range(CASTLE_VAL)]
        self.ep: list = [self.rand64() for _ in range(BOARD_SQ_NUM)]

    def rand64(self):
        return uuid1().int >> 64

class MovesStruct:
    def __init__(self) -> None:
        self.moves:list = [move_t(-1) for _ in range(GEN_STACK)]
        self.count:int = 0

class BoardState:
    def __init__(self) -> None:
        self.zobrist = Zobrist()
        self.hash_key: int = 0
        self.nodes: int = 0
        self.parsed_fen: str = ''
        self.king_square: list = [squares['e8'], squares['e1']]
        self.side: int = -1
        self.xside: int = -1
        self.castle: int = 15
        self.enpassant: int = squares['OFFBOARD']
        self.pce_count: list = [0 for _ in range(PIECE_TYPES)]
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
            if not (sq & 0x88):
                piece:int = self.board[sq]
                if piece: self.hash_key ^= self.zobrist.piecesquare[piece][sq]

        if self.enpassant != squares['OFFBOARD']: self.hash_key ^= self.zobrist.ep[self.enpassant]
        self.hash_key ^= self.zobrist.castling[self.castle]
        if not self.side: self.hash_key ^= self.zobrist.side

    def init_state(self, fen:str) -> None:
        self.pce_count = [0 for _ in range(PIECE_TYPES)]
        self.hash_key = 0
        self.nodes = 0
        self.parsed_fen = ''
        self.king_square = [squares['e8'], squares['e1']]
        self.side: int = -1
        self.xside: int = -1
        self.castle: int = 15
        self.enpassant: int = squares['OFFBOARD']
        self.parse_fen(fen)
        self.gen_hashkey()

    def clear_board(self) -> None:
        # sweep the surface clean
        for rank in range(8):
            for file in range(16):
                square:int = rank * 16 + file
                if not (square & 0x88):
                    self.board[square] = e

        self.pce_count = [0 for _ in range(PIECE_TYPES)]
        self.hash_key = 0
        self.nodes = 0
        self.parsed_fen = ''
        self.king_square = [squares['e8'], squares['e1']]
        self.side: int = -1
        self.xside: int = -1
        self.castle: int = 15
        self.enpassant: int = squares['OFFBOARD']

    def generate_fen(self) -> str:
        fen_string: str = ''
        empty: int = 0

        # filling up the string with pieces
        for r in range(8):
            for f in range(16):
                sq = r * 16 + f
                if not (sq & 0x88):
                    if self.board[sq] == e: empty += 1
                    elif 1 <= self.board[sq] <= 12:
                        if empty:
                            fen_string = f'{fen_string}{empty}'
                            empty = 0
                        fen_string = f'{fen_string}{int_pieces[self.board[sq]]}'
            if empty:
                fen_string = f'{fen_string}{empty}'
                empty = 0
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
                    square:int = rank * 16 + file
                    if not (square & 0x88):
                        if 1 <= char_pieces[sym] <= 12:
                            self.pce_count[char_pieces[sym]] += 1
                            if sym == 'K': self.king_square[sides['white']] = square
                            elif sym == 'k': self.king_square[sides['black']] = square
                            self.board[square] = char_pieces[sym]
                        file += 1

        # choose which side goes first
        if fen_segments[1] == 'w':
            self.side = sides['white']
            self.xside = sides['black']
        elif fen_segments[1] == 'b':
            self.side = sides['black']
            self.xside = sides['white']
        else:
            self.side = -1
            self.xside = -1

        # castle rights parsing
        for sym in fen_segments[2]:
            if sym == '-': break
            elif sym == 'K': self.castle |= castling_vals['K']
            elif sym == 'Q': self.castle |= castling_vals['Q']
            elif sym == 'k': self.castle |= castling_vals['k']
            elif sym == 'q': self.castle |= castling_vals['q']

        # load enpassant square
        fen_ep:str = fen_segments[3]
        if fen_ep != '-':
            file:int = ord(fen_ep[0]) - ord('a')
            rank:int = 8 - (ord(fen_ep[1]) - ord('0'))
            self.enpassant = rank * 16 + file
        else: self.enpassant = squares['OFFBOARD']




    def is_square_attacked(self, square:int, side:int) -> int:
        # pawn attacks
        if side:
            if not (square + 17) & 0x88 and self.board[square + 17] == P: return 1
            if not (square + 15) & 0x88 and self.board[square + 15] == P: return 1
        else:
            if not (square - 17) & 0x88 and self.board[square - 17] == p: return 1
            if not (square - 15) & 0x88 and self.board[square - 15] == p: return 1

        # knight attacks
        for i in range(8):
            target_sq:int = square + knight_offsets[i]
            if 0 <= target_sq <= 127:
                target_piece:int = self.board[target_sq]
                if not (target_sq & 0x88):
                    if (target_piece == N) if side else (target_piece == n): return 1

        # king attacks
        for i in range(8):
            target_sq:int = square + king_offsets[i]
            if 0 <= target_sq <= 127:
                target_piece:int = self.board[target_sq]
                if not (target_sq & 0x88):
                    if (target_piece == K) if side else (target_piece == k): return 1

        # bishop attacks
        for i in range(4):
            target_sq:int = square + bishop_offsets[i]
            while not (target_sq & 0x88):
                if 0 <= target_sq <= 127:
                    target_piece:int = self.board[target_sq]
                    if (target_piece == B or target_piece == Q) if side else (target_piece == b or target_piece == q): return 1
                    if target_piece: break
                    target_sq += bishop_offsets[i]

        # rook attacks
        for i in range(4):
            target_sq:int = square + rook_offsets[i]
            while not (target_sq & 0x88):
                if 0 <= target_sq <= 127:
                    target_piece:int = self.board[target_sq]
                    if (target_piece == R or target_piece == Q) if side else (target_piece == r or target_piece == q): return 1
                    if target_piece: break
                    target_sq += rook_offsets[i]
        return 0


    def make_move(self, move:int, capture_flag:int) -> int: # bound to return a int, in replacement for bool

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

            # get move source and the square it moves to
            from_square:int = get_move_source(move)
            to_square:int = get_move_target(move)
            promoted_piece:int = get_move_piece(move)
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

            # adjusting board state
            if captured_piece:
                self.hash_key ^= self.zobrist.piecesquare[captured_piece][to_square]
                self.pce_count[captured_piece] -= 1
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
            if self.enpassant != squares['OFFBOARD']: self.hash_key ^= self.zobrist.ep[self.enpassant]
            self.enpassant = squares['OFFBOARD']
            if double_push:
                self.enpassant = to_square + 16 if self.side else to_square - 16
                if self.side: self.hash_key ^= self.zobrist.ep[to_square + 16]
                else: self.hash_key ^= self.zobrist.ep[to_square - 16]
            if castling:
                if to_square == squares['g1']:
                    self.board[squares['f1']] = self.board[squares['h1']]
                    self.board[squares['h1']] = e
                    self.hash_key ^= self.zobrist.piecesquare[R][squares['h1']]
                    self.hash_key ^= self.zobrist.piecesquare[R][squares['f1']]
                elif to_square == squares['c1']:
                    self.board[squares['d1']] = self.board[squares['a1']]
                    self.board[squares['a1']] = e
                    self.hash_key ^= self.zobrist.piecesquare[R][squares['a1']]
                    self.hash_key ^= self.zobrist.piecesquare[R][squares['d1']]
                elif to_square == squares['g8']:
                    self.board[squares['f8']] = self.board[squares['h8']]
                    self.board[squares['h8']] = e
                    self.hash_key ^= self.zobrist.piecesquare[r][squares['h8']]
                    self.hash_key ^= self.zobrist.piecesquare[r][squares['f8']]
                elif to_square == squares['c8']:
                    self.board[squares['d8']] = self.board[squares['a8']]
                    self.board[squares['a8']] = e
                    self.hash_key ^= self.zobrist.piecesquare[r][squares['a8']]
                    self.hash_key ^= self.zobrist.piecesquare[r][squares['d1']]

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

            # take back move if king is under attack
            if self.is_square_attacked(self.king_square[self.xside], self.side):
                self.board = [_ for _ in board_cpy]
                self.side = side_cpy
                self.xside = xside_cpy
                self.enpassant = enpassant_cpy
                self.castle = castle_cpy
                self.king_square = [_ for _ in king_square_cpy]
                self.pce_count = [_ for _ in pce_count_cpy]
                self.hash_key = hashkey_cpy
                return 0 # illegal
            else: return 1 # legal
        elif capture_flag == CAPTURE_MOVES:
            if get_move_capture(move): self.make_move(move, ALL_MOVES)
            else: return 0 # move is not a capture
        return 0 # shouldn't reach here

    def add_move(self, move_list: MovesStruct, move: int) -> None:
        move_list.moves[move_list.count].move = move
        move_list.count += 1

    def gen_moves(self, move_list: MovesStruct) -> None:
        move_list.count = 0
        for sq in range(BOARD_SQ_NUM):
            if not (sq & 0x88):
                if self.side:
                    if self.board[sq] == P:
                        to_sq:int = sq - 16
                        if not (to_sq & 0x88) and not self.board[to_sq]:
                            if sq >= squares['a7'] and sq <= squares['h7']:
                                self.add_move(move_list, encode_move(sq, to_sq, Q, 0, 0, 0, 0))
                                self.add_move(move_list, encode_move(sq, to_sq, R, 0, 0, 0, 0))
                                self.add_move(move_list, encode_move(sq, to_sq, B, 0, 0, 0, 0))
                                self.add_move(move_list, encode_move(sq, to_sq, N, 0, 0, 0, 0))
                            else:
                                self.add_move(move_list, encode_move(sq, to_sq, 0, 0, 0, 0, 0))
                                if sq >= squares['a2'] and sq <= squares['h2'] and not self.board[sq - 32]:
                                    self.add_move(move_list, encode_move(sq, sq - 32, 0, 0, 1, 0, 0))
                        for i in range(4):
                            pawn_offset:int = bishop_offsets[i]
                            if pawn_offset < 0:
                                to_sq:int = sq + pawn_offset
                                if not (to_sq & 0x88):
                                    if (sq >= squares['a7'] and sq <= squares['h7']) and\
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
                            if not self.board[squares['f1']] and not self.board[squares['g1']]:
                                if not self.is_square_attacked(squares['e1'], sides['black']) and not self.is_square_attacked(squares['f1'], sides['black']):
                                    self.add_move(move_list, encode_move(squares['e1'], squares['g1'], 0, 0, 0, 0, 1))
                        if self.castle & castling_vals['Q']:
                            if not self.board[squares['d1']] and not self.board[squares['b1']] and not self.board[squares['c1']]:
                                if not self.is_square_attacked(squares['e1'], sides['black']) and not self.is_square_attacked(squares['d1'], sides['black']):
                                    self.add_move(move_list, encode_move(squares['e1'], squares['c1'], 0, 0, 0, 0, 1))
                else:
                    if self.board[sq] == p:
                        to_sq:int = sq + 16
                        if not (to_sq & 0x88) and not self.board[to_sq]:
                            if sq >= squares['a2'] and sq <= squares['h2']:
                                self.add_move(move_list, encode_move(sq, to_sq, q, 0, 0, 0, 0))
                                self.add_move(move_list, encode_move(sq, to_sq, r, 0, 0, 0, 0))
                                self.add_move(move_list, encode_move(sq, to_sq, b, 0, 0, 0, 0))
                                self.add_move(move_list, encode_move(sq, to_sq, n, 0, 0, 0, 0))
                            else:
                                self.add_move(move_list, encode_move(sq, to_sq, 0, 0, 0, 0, 0))
                                if sq >= squares['a7'] and sq <= squares['h7'] and not self.board[sq + 32]:
                                    self.add_move(move_list, encode_move(sq, sq + 32, 0, 0, 1, 0, 0))
                        for i in range(4):
                            pawn_offset:int = bishop_offsets[i]
                            if pawn_offset > 0:
                                to_sq = sq + pawn_offset
                                if not (to_sq & 0x88):
                                    if (sq >= squares['a2'] and sq <= squares['h2']) and\
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
                            if not self.board[squares['f8']] and not self.board[squares['g8']]:
                                if not self.is_square_attacked(squares['e8'], sides['white']) and not self.is_square_attacked(squares['f8'], sides['white']):
                                    self.add_move(move_list, encode_move(squares['e8'], squares['g8'], 0, 0, 0, 0, 1))
                        if self.castle & castling_vals['q']:
                            if not self.board[squares['d8']] and not self.board[squares['b8']] and not self.board[squares['c8']]:
                                if not self.is_square_attacked(squares['e8'], sides['white']) and not self.is_square_attacked(squares['d8'], sides['white']):
                                    self.add_move(move_list, encode_move(squares['e8'], squares['c8'], 0, 0, 0, 0, 1))

                if (self.board[sq] == N) if self.side else (self.board[sq] == n):
                    for i in range(8):
                        to_sq:int = sq + knight_offsets[i]
                        if 0 <= to_sq < BOARD_SQ_NUM:
                            piece:int = self.board[to_sq]
                            if not (to_sq & 0x88):
                                if (not piece or (piece >= 7 and piece <= 12)) if self.side else\
                                    (not piece or (piece >= 1 and piece <= 6)):
                                    if piece:
                                        self.add_move(move_list, encode_move(sq, to_sq, 0, 1, 0, 0, 0))
                                    else: self.add_move(move_list, encode_move(sq, to_sq, 0, 0, 0, 0, 0))

                if (self.board[sq] == K) if self.side else (self.board[sq] == k):
                    for i in range(8):
                        to_sq:int = sq + king_offsets[i]
                        if 0 <= to_sq < BOARD_SQ_NUM:
                            piece:int = self.board[to_sq]
                            if not (to_sq & 0x88):
                                if (not piece or (piece >= 7 and piece <= 12)) if self.side else\
                                    (not piece or (piece >= 1 and piece <= 6)):
                                    if piece:
                                        self.add_move(move_list, encode_move(sq, to_sq, 0, 1, 0, 0, 0))
                                    else: self.add_move(move_list, encode_move(sq, to_sq, 0, 0, 0, 0, 0))

                if ((self.board[sq] == B) or (self.board[sq] == Q)) if self.side\
                    else ((self.board[sq] == b) or (self.board[sq] == q)):
                    for i in range(4):
                        to_sq:int = sq + bishop_offsets[i]
                        while not (to_sq & 0x88):
                            if 0 <= to_sq <= 127:
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
                        while not (to_sq & 0x88):
                            if 0 <= to_sq <= 127:
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

    def perft_test(self, depth:int) -> None:
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

            curr_elapsed:float = perf_counter() - start_time

            if get_move_piece(move_list.moves[mv_count].move): print(f'  {square_to_coords[get_move_source(move_list.moves[mv_count].move)]}{square_to_coords[get_move_target(move_list.moves[mv_count].move)]}{promoted_pieces[get_move_piece(move_list.moves[mv_count].move)]}:   {old_nodes}   nps: {int(self.nodes//curr_elapsed)}')
            else: print(f'  {square_to_coords[get_move_source(move_list.moves[mv_count].move)]}{square_to_coords[get_move_target(move_list.moves[mv_count].move)]}:   {old_nodes}   nps: {int(self.nodes//curr_elapsed)}')

        elapsed:float = perf_counter() - start_time
        print(f'\n  [SEARCH TIME]: {round(elapsed * 1000)} ms, {elapsed} sec')
        print(f'  [DEPTH SEARCHED]: {depth} ply')
        print(f'  [TOTAL NODES]: {self.nodes} nodes')
        print(f'  [NPS]: {int(self.nodes//elapsed)} nps\n')

    def test_suite(self) -> None:
        for depth in range(4):
            self.perft_test(depth)

    def print_board(self) -> None:
        print('\n________________________________\n\n')
        for rank in range(8):
            for file in range(16):
                square:int = rank * 16 + file
                if file == 0:
                    print('     ', 8 - rank, end='  ')
                if not (square & 0x88):
                    print(ascii_pieces[self.board[square]], end=' ')
            print()
        print('\n         a b c d e f g h\n')
        print('________________________________\n')
        print(f'  [SIDE TO MOVE]: {"white" if self.side else "black"} | {self.side}')
        print('  [CURRENT CASTLING RIGHTS]: {}{}{}{} | {}'.format(
                'K' if (self.castle & castling_vals['K']) else '-',
                'Q' if (self.castle & castling_vals['Q']) else '-',
                'k' if (self.castle & castling_vals['k']) else '-',
                'q' if (self.castle & castling_vals['q']) else '-',
                self.castle,
            ))
        if self.enpassant != squares['OFFBOARD']: print(f'  [ENPASSANT TARGET SQUARE]: {square_to_coords[self.enpassant]} | {self.enpassant}')
        else: print(f'  [ENPASSANT TARGET SQUARE]: NONE | {self.enpassant}')
        print(f'  [KING SQUARE]: {square_to_coords[self.king_square[self.side]]} | {self.king_square[self.side]}')
        print(f'  [PARSED FEN]: {self.parsed_fen}')

def print_move_list(move_list, mode:str):
    if mode == 'full':
        print('\nMOVE   CAPTURE   DOUBLE   ENPASS   CASTLING\n')
    else: print()
    for idx in range(move_list.count):
        move:int = move_list.moves[idx].move
        if move is None: continue
        formated_move:str = f'{square_to_coords[get_move_source(move)]}{square_to_coords[get_move_target(move)]}'
        promotion_move:str = promoted_pieces[get_move_piece(move)] if get_move_piece(move) else ' '
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
