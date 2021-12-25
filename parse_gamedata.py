
import os
import chess.pgn
import numpy as np


def get_dataset():
    vals = {'1/2-1/2': 0, '0-1': -1, '1-0': 1}
    processed_file = open('processed/openings.txt', 'w+')
    for fn in os.listdir('data'):
        pgn = open(os.path.join('data', fn))
        while 1:
            print('----------------------------------------------------------------')
            game = chess.pgn.read_game(pgn)
            if game is None:
                break

            res = game.headers['Result']
            if res not in vals:
                continue

            val = vals[res]
            board = game.board()
            for i, move in enumerate(game.mainline_moves()):
                board.push(move)
                processed_file.write(str(move) + ' ')
                print(move)

            processed_file.write('\n')


if __name__ == '__main__':
    get_dataset()
