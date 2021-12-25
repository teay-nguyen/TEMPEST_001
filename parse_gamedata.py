
import os
import chess.pgn
import chess


def get_dataset():
    vals = {'1/2-1/2': 0, '0-1': -1, '1-0': 1}
    processed_file = open('processed/openings.txt', 'w+')
    gn = 0
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

            board = game.board()
            for move in game.mainline_moves():
                board.push(move)
                processed_move = chess.Move.from_uci(str(move))
                processed_file.write(str(processed_move) + ' ')

            processed_file.write(res + '\n')
            gn += 1
            print(f'PARSING GAME FINISHED, PARSING NEXT GAME: {gn}')

    print('FINISHED PARSING GAME DATA AND WRITING TO TEXT FILE...')


if __name__ == '__main__':
    get_dataset()
