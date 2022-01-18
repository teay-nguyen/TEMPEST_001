#!/usr/bin/env python3 -u

'''
************************************************************************************************************

                                        The Pioneer Chess Engine
                                                (0x88)

                                                  by

                                            HashHobo (Terry)


    - 0x88 board representation
    - I, HashHobo was daring enough to try make a world class chess engine using PYTHON (well, thought speed wasn't everything, I guess it is everything in a chess engine)
    - AlphaBeta, no parallel search though, maybe PVS search, idk, I might try other search techniques
    - Hot features such as zobrist hashing and transposition tables (well not really, it's kinda basic in a chess engine)
    - I will attempt implementing a few search pruning techniques, but its kinda hard
    - Board is representated by numbers, masked by characters in a table

************************************************************************************************************
'''

'''
************************************************************************************************************

                                            PYTHON EDITION v2.0

    - This is also my very first implementation of the Pioneer engine
    - Probably gonna work on a C++ or C# implementation of this on a later date
    - The engine is obviously weaker than other popular engines because Python, so don't expect superb performance
    - I actually document or keep my older implementations of this, so you can check it out and probably send a PR if you want
    - This is a project for fun, also my first major project of my life, since I was 13 since I started working on this
    - I put the first version in the old trash implementation folder because it is indeed trash anyways

************************************************************************************************************
'''

# piece encoding
e, P, N, B, R, Q, K, p, n, b, r, q, k, o = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13
ascii_pieces:str = '.PNBRQKpnbrqko'
unicode_pieces:str = '.♙♘♗♖♕♔p♞♝♜♛♚'

squares:dict = {
        "a8":0, "b8":1, "c8":2, "d8":3, "e8":4, "f8":5, "g8":6, "h8":7,
        "a7":16, "b7":17, "c7":18, "d7":19, "e7":20, "f7":21, "g7":22, "h7":23,
        "a6":32, "b6":33, "c6":34, "d6":35, "e6":36, "f6":37, "g6":38, "h6":39,
        "a5":48, "b5":49, "c5":50, "d5":51, "e5":52, "f5":53, "g5":54, "h5":55,
        "a4":64, "b4":65, "c4":66, "d4":67, "e4":68, "f4":69, "g4":70, "h4":71,
        "a3":80, "b3":81, "c3":82, "d3":83, "e3":84, "f3":85, "g3":86, "h3":87,
        "a2":96, "b2":97, "c2":98, "d2":99, "e2":100, "f2":101, "g2":102, "h2":103,
        "a1":112, "b1":113, "c1":114, "d1":115, "e1":116, "f1":117, "g1":118, "h1":119, "null_sq":120,
}

square_to_coords:list = [
    "a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8", "i8", "j8", "k8", "l8", "m8", "n8", "o8", "p8",
    "a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7", "i7", "j7", "k7", "l7", "m7", "n7", "o7", "p7",
    "a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6", "i6", "j6", "k6", "l6", "m6", "n6", "o6", "p6",
    "a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5", "i5", "j5", "k5", "l5", "m5", "n5", "o5", "p5",
    "a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4", "i4", "j4", "k4", "l4", "m4", "n4", "o4", "p4",
    "a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3", "i3", "j3", "k3", "l3", "m3", "n3", "o3", "p3",
    "a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2", "i2", "j2", "k2", "l2", "m2", "n2", "o2", "p2",
    "a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1", "i1", "j1", "k1", "l1", "m1", "n1", "o1", "p1",
]

char_pieces:dict = {
    'P':P, 'N':N, 'B':B, 'R':R, 'Q':Q, 'K':K, 'p':p, 'n':n, 'b':b, 'r':r, 'q':q, 'k':k,
}

'''
    Decided to comment stuff because short term memory really kills me in these situations

    bin   dec
    0001  1    white king to king side
    0010  2    white king to queen side
    0100  4    black king to king side
    1000  8    black king to queen side
'''

# initial values
sides:dict = {'white':1, 'black':0}
castling:dict = {'K':1, 'Q':2, 'k':4, 'q':8}

# fen debug positions
start_position:str = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
custom_endgame_position:str = '8/5R2/8/k7/1r6/4K3/6R1/8 w - - 0 1'
custom_middlegame_position:str = 'r1bq1rk1/ppp1bppp/2n2n2/3pp3/2BPP3/2N1BN2/PP3PPP/R2Q1RK1 w - - 0 1'
empty_board:str = '8/8/8/8/8/8/8/8 w - - 0 1'

# piece movement offsets
knight_offsets:tuple = (33, 31, 18, 14, -33, -31, -18, -14)
bishop_offsets:tuple = (15, 17, -15, -17)
rook_offsets:tuple = (16, 1, -16, -1)
king_offsets:tuple = (16, 1, -16, -1, 15, 17, -15, -17)

# main driver
class board:
    def __init__(self) -> None:
        self.side = None
        self.castle = 0
        self.enpassant = squares['null_sq']
        self.board = [ # initialized with the start position so things can be easier
            r, n, b, q, k, b, n, r,  o, o, o, o, o, o, o, o,
            p, p, p, p, p, p, p, p,  o, o, o, o, o, o, o, o,
            e, e, e, e, e, e, e, e,  o, o, o, o, o, o, o, o,
            e, e, e, e, e, e, e, e,  o, o, o, o, o, o, o, o,
            e, e, e, e, e, e, e, e,  o, o, o, o, o, o, o, o,
            e, e, e, e, e, e, e, e,  o, o, o, o, o, o, o, o,
            P, P, P, P, P, P, P, P,  o, o, o, o, o, o, o, o,
            R, N, B, Q, K, B, N, R,  o, o, o, o, o, o, o, o,
        ]

    def clear_board(self):
        for rank in range(8):
            for file in range(16):
                square = self.conv_rf_idx(rank, file)
                if (not (square & 0x88)):
                    self.board[square] = e

        self.side = None
        self.castle = 0
        self.enpassant = squares['null_sq']

    def parse_fen(self, fen:str):
        # clear board before parsing string
        self.clear_board()

        # load pieces onto board
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
                    assert (ord('a') <= ord(sym) <= ord('z')) or (ord('A') <= ord(sym) <= ord('Z'))
                    square = self.conv_rf_idx(rank, file)
                    if (not (square & 0x88)):
                        self.board[square] = char_pieces[sym]
                        file += 1

        # choose which side goes first
        fen_side = fen_segments[1]
        if fen_side == 'w':
            self.side = sides['white']
        elif fen_side == 'b':
            self.side = sides['black']
        else:
            self.side = None

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

    def conv_rf_idx(self, rank:int, file:int):
        return rank * 16 + file

    def generate_attacks(self, square, side):
        # pawn attacks
        if (side):
            if (not ((square + 17) & 0x88) and (self.board[square + 17] == P)):
                return 1
            if (not ((square + 15) & 0x88) and (self.board[square + 15] == P)):
                return 1
        else:
            if (not ((square - 17) & 0x88) and (self.board[square - 17] == p)):
                return 1
            if (not ((square - 15) & 0x88) and (self.board[square - 15] == p)):
                return 1
        
        # knight attacks
        for i in range(8):
            target_sq = square + knight_offsets[i]
            if 0 <= target_sq <= 127:
                target_piece = self.board[target_sq]
                if (not (target_sq & 0x88)):
                    if ((target_piece == N) if side else (target_piece == n)):
                        return 1

        for i in range(8):
            target_sq = square + king_offsets[i]
            if 0 <= target_sq <= 127:
                target_piece = self.board[target_sq]
                if (not (target_sq & 0x88)):
                    if ((target_piece == K) if side else (target_piece == k)):
                        return 1

        return 0

    def print_board(self):
        print()
        for rank in range(8):
            for file in range(16):
                square = self.conv_rf_idx(rank, file)
                if (file == 0):
                    print(8 - rank, end='  ')
                if (not (square & 0x88)):
                    print(ascii_pieces[self.board[square]], end=' ')
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
        if square_to_coords[self.enpassant] != 'i1':
            print(f'[ENPASSANT TARGET SQUARE]: {square_to_coords[self.enpassant]}\n')
        else: print(f'[ENPASSANT TARGET SQUARE]: NONE')

    def print_attack_map(self, side:int):
        print()
        for rank in range(8):
            for file in range(16):
                square = self.conv_rf_idx(rank, file)
                if (file == 0):
                    print(8 - rank, end='  ')
                if (not (square & 0x88)):
                    print('x' if self.generate_attacks(square, side) else '.', end=' ')
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
        if square_to_coords[self.enpassant] != 'i1':
            print(f'[ENPASSANT TARGET SQUARE]: {square_to_coords[self.enpassant]}\n')
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
        if square_to_coords[self.enpassant] != 'i1':
            print(f'[ENPASSANT TARGET SQUARE]: {square_to_coords[self.enpassant]}\n')
        else: print(f'[ENPASSANT TARGET SQUARE]: NONE')

bboard = board()
bboard.parse_fen('8/8/8/3K4/8/8/8/8 w KQkq g5 0 1')
bboard.print_board()
bboard.print_attack_map(sides['white'])
