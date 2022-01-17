
'''

************************************************************************************************************

    The Pioneer Chess Engine
            (0x88)

              by

       HashHobo (Terry)


    - 0x88 board representation
    - I, HashHobo was dumb enough to try make a world class chess engine using PYTHON
    - AlphaBeta, no parallel search though, maybe PVS search, idk, I might try other search techniques
    - Hot features such as zobrist hashing and transposition tables (Well not really)

************************************************************************************************************

'''

# piece encoding
e, P, N, B, R, Q, K, p, n, b, r, q, k, o = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13
ascii_pieces = '.PNBRQKpnbrqko'
unicode_pieces = '.♙♘♗♖♕♔p♞♝♜♛♚'
squares = {
        "a8":0, "b8":1, "c8":2, "d8":3, "e8":4, "f8":5, "g8":6, "h8":7,
        "a7":16, "b7":17, "c7":18, "d7":19, "e7":20, "f7":21, "g7":22, "h7":23,
        "a6":32, "b6":33, "c6":34, "d6":35, "e6":36, "f6":37, "g6":38, "h6":39,
        "a5":48, "b5":49, "c5":50, "d5":51, "e5":52, "f5":53, "g5":54, "h5":55,
        "a4":64, "b4":65, "c4":66, "d4":67, "e4":68, "f4":69, "g4":70, "h4":71,
        "a3":80, "b3":81, "c3":82, "d3":83, "e3":84, "f3":85, "g3":86, "h3":87,
        "a2":96, "b2":97, "c2":98, "d2":99, "e2":100, "f2":101, "g2":102, "h2":103,
        "a1":112, "b1":113, "c1":114, "d1":115, "e1":116, "f1":117, "g1":118, "h1":119,
}
square_to_coords = [
    "a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8", "i8", "j8", "k8", "l8", "m8", "n8", "o8", "p8",
    "a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7", "i7", "j7", "k7", "l7", "m7", "n7", "o7", "p7",
    "a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6", "i6", "j6", "k6", "l6", "m6", "n6", "o6", "p6",
    "a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5", "i5", "j5", "k5", "l5", "m5", "n5", "o5", "p5",
    "a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4", "i4", "j4", "k4", "l4", "m4", "n4", "o4", "p4",
    "a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3", "i3", "j3", "k3", "l3", "m3", "n3", "o3", "p3",
    "a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2", "i2", "j2", "k2", "l2", "m2", "n2", "o2", "p2",
    "a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1", "i1", "j1", "k1", "l1", "m1", "n1", "o1", "p1",
]
char_pieces = {
    'P':P, 'N':N, 'B':B, 'R':R, 'Q':Q, 'K':K, 'p':p, 'n':n, 'b':b, 'r':r, 'q':q, 'k':k,
}

# fen debug positions
start_position = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
custom_endgame_position = '8/5R2/8/k7/1r6/4K3/6R1/8 w - - 0 1'
custom_middlegame_position = 'r1bq1rk1/ppp1bppp/2n2n2/3pp3/2BPP3/2N1BN2/PP3PPP/R2Q1RK1 w - - 0 1'

# main driver
class board:
    def __init__(self) -> None:
        self.board = [
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

    def parse_fen(self, fen):
        self.clear_board()
        
        fen_pieces = fen.split()[0]
        rank, file = 0, 0

    def conv_rf_idx(self, rank, file):
        return rank * 16 + file

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
        print('\n   a b c d e f g h')

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
        print('\n   a b c d e f g h')

bboard = board()
bboard.clear_board()
bboard.print_board()
