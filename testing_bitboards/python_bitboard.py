from ctypes import c_ulonglong as ull

a8, b8, c8, d8, e8, f8, g8, h8 =         0, 1, 2, 3, 4, 5, 6, 7
a7, b7, c7, d7, e7, f7, g7, h7 =   8, 9, 10, 11, 12, 13, 14, 15
a6, b6, c6, d6, e6, f6, g6, h6 = 16, 17, 18, 19, 20, 21, 22, 23
a5, b5, c5, d5, e5, f5, g5, h5 = 24, 25, 26, 27, 28, 29, 30, 31
a4, b4, c4, d4, e4, f4, g4, h4 = 32, 33, 34, 35, 36, 37, 38, 39
a3, b3, c3, d3, e3, f3, g3, h3 = 40, 41, 42, 43, 44, 45, 46, 47
a2, b2, c2, d2, e2, f2, g2, h2 = 48, 49, 50, 51, 52, 53, 54, 55
a1, b1, c1, d1, e1, f1, g1, h1 = 56, 57, 58, 59, 60, 61, 62, 63

def set_bit(bitboard, square): bitboard |= (ull(1) << square)
def get_bit(bitboard, square): return bitboard & (ull(1) << square)
def pop_bit(bitboard, square): bitboard ^= ((ull(1) << square) if get_bit(bitboard, square) else 0)

def print_bitboard(bitboard):
    print()
    for rank in range(8):
        for file in range(8):
            square = rank * 8 + file
            if not file:
                print(f'    {8 - rank} ')
            print(f' {1 if get_bit(bitboard, square) else 0}')
        print()
    print('\n     a b c d e f g h\n')
    print(f'    Bitboard: {bitboard}')

if __name__ == '__main__':
    bitboard = ull(0)
    set_bit(bitboard, e4)
    set_bit(bitboard, c3)
    set_bit(bitboard, f2)
    print_bitboard(bitboard)
    pop_bit(bitboard, e4)
    print_bitboard(bitboard)
