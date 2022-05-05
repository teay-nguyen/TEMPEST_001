#!/usr/bin/env pypy3 -u
# -*- coding: utf-8 -*-


'''

    MIGHT NOT NEED THIS FILE, BUT ILL KEEP IT

'''

import os
import chess.pgn
import chess

processed_file = open('processed/openings.txt', 'w+')

def get_dataset():
    vals:dict = {'1/2-1/2':0, '0-1':-1, '1-0':1}
    gn = 0
    for fn in os.listdir('data_folder'):
        pgn = open(os.path.join('data_folder', fn))
        while 1:
            game = chess.pgn.read_game(pgn)

            if game is None: break

            res = game.headers['Result']
            if res not in vals: continue

            board = game.board()
            for move in game.mainline_moves():
                board.push(move)
                processed_move = chess.Move.from_uci(str(move))
                processed_file.write(str(processed_move) + ' ')

            processed_file.write(res + '\n')
            gn += 1
            print('[FINISHED PARSING GAME, PREPARING NEXT GAME]:', gn)
        print('[FINISHED PARSING FILE AND WRITING TO TEXT FILE...]')
    print('[PROCESSED FILE IS READY FOR USAGE...]')
    print('[PROCESSED FILE IS LOCATED IN DIRECTORY: processed/openings.txt]')

if __name__ == '__main__':
    get_dataset()
