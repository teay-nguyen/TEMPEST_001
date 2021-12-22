
positions = {}
piece_nums = {
    'K': '2',
    'Q': '3',
    'R': '4',
    'B': '5',
    'N': '6',
    'p': '7',
    '-': '8',
}

sides = {
    'b': '1',
    'w': '0',
    '-': '2'
}


class Zobrist:
    def __init__(self):
        pass

    def hash(self, state):
        board = state.board
        hashed_string = ''
        for row in range(len(board)):
            for col in range(len(board[row])):
                piece = board[row, col]
                piece_type = piece[1]
                piece_side = piece[0]
                full = sides[piece_side] + piece_nums[piece_type]

                hashed_string += full

        length_hashed = len(hashed_string)
        print(hashed_string, length_hashed)
