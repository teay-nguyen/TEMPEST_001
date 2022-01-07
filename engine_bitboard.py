import numpy as np

class Board:

    '''
        ENGINE BITBOARD (ALTERNATIVE TO THE REGULAR ONE)
        - alternative to regular state, which is slower than my grandma
        - function setting start state
        - new hot features and optimizations such as bits and faster move generation
        - maybe function to map fen to board state

        - numpy and bitwise stuff to minimize memory allocation

    '''

    def __init__(self):
        self.white_king_bitboard = self.create_empty_bitmap()
        self.white_queen_bitboard = self.create_empty_bitmap()
        self.white_rook_bitboard = self.create_empty_bitmap()
        self.white_bishop_bitboard = self.create_empty_bitmap()
        self.white_knight_bitboard = self.create_empty_bitmap()
        self.white_pawn_bitboard = self.create_empty_bitmap()

        self.black_king_bitboard = self.create_empty_bitmap()
        self.black_queen_bitboard = self.create_empty_bitmap()
        self.black_rook_bitboard = self.create_empty_bitmap()
        self.black_bishop_bitboard = self.create_empty_bitmap()
        self.black_knight_bitboard = self.create_empty_bitmap()
        self.black_pawn_bitboard = self.create_empty_bitmap()

        self.init_start_position()

        self.bitboards = np.vstack((
            self.white_rook_bitboard,
            self.white_knight_bitboard,
            self.white_bishop_bitboard,
            self.white_queen_bitboard,
            self.white_king_bitboard,
            self.white_pawn_bitboard,
            self.black_rook_bitboard,
            self.black_knight_bitboard,
            self.black_bishop_bitboard,
            self.black_queen_bitboard,
            self.black_king_bitboard,
            self.black_pawn_bitboard,

        ))

    def update_bitboard_state(self):
        res = np.zeros(64, dtype='byte')
        for board in self.bitboards:
            res = np.bitwise_or(board, res, dtype='byte')

        self.bitboards = res

    def pprint_bitboard(self):
        val = ''
        for i, square in enumerate(self.bitboards):
            if not i % 8:
                val += '\n'
            if square:
                val += 'X'
                continue
            val += '-'

        print(val)

    def create_empty_bitmap(self):
        return np.zeros(64, dtype='byte')

    def init_start_position(self):
        self.white_rook_bitboard[0] = 1
        self.white_rook_bitboard[7] = 1
        self.white_knight_bitboard[1] = 1
        self.white_knight_bitboard[6] = 1
        self.white_bishop_bitboard[2] = 1
        self.white_bishop_bitboard[5] = 1
        self.white_queen_bitboard[4] = 1
        self.white_king_bitboard[3] = 1

        for i in range(8, 16):
            self.white_pawn_bitboard[i] = 1

        self.black_rook_bitboard[63] = 1
        self.black_rook_bitboard[56] = 1
        self.black_knight_bitboard[57] = 1
        self.black_knight_bitboard[62] = 1
        self.black_bishop_bitboard[61] = 1
        self.black_bishop_bitboard[58] = 1
        self.black_queen_bitboard[59] = 1
        self.black_king_bitboard[60] = 1

        for i in range(48, 56):
            self.black_pawn_bitboard[i] = 1
