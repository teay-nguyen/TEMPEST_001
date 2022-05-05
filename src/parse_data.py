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
    for fn in os.listdir('pgn_folder'):
        pgn = open(os.path.join('pgn_folder', fn))
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
