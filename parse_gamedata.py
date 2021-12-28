
import os
import chess.pgn
import chess
from multiprocessing import Pool

processed_file = open('processed/openings.txt', 'w+')

def get_dataset():
    vals = {'1/2-1/2': 0, '0-1': -1, '1-0': 1}
    gn = 0
    for fn in os.listdir('data'):
        pgn = open(os.path.join('data', fn))
        while 1:
            game = chess.pgn.read_game(pgn)
            if game is None:
                break

            res = game.headers['Result']
            if res not in vals:
                continue

            board = game.board()
            for move in game.mainline_moves():
                board.push(move)
                processed_move = chess.Move.from_uci(str(move))
                processed_file.write(str(processed_move) + ' ')

            processed_file.write(res + '\n')
            gn += 1
            print('PARSING GAME FINISHED, PARSING NEXT GAME:', gn)

    print('FINISHED PARSING GAME DATA AND WRITING TO TEXT FILE...')

def parse_game(file):
    pgn = open(os.path.join('data', file))
    while 1:
        game = chess.pgn.read_game(pgn)
        if game is None:
            return

        res = game.headers['Result']

        board = game.board()
        for move in game.mainline_moves():
            board.push(move)
            processed_move = chess.Move.from_uci(str(move))
            processed_file.write(str(processed_move) + ' ')

        processed_file.write(res + '\n')
        print('PARSING GAME FINISHED, PARSING NEXT GAME...')

if __name__ == '__main__':
    pool = Pool()
    pool.map(parse_game, [fn for fn in os.listdir('data')])
