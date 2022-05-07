#!/usr/bin/env pypy3
# -*- coding: utf-8 -*-

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

import sys
from board0x88 import BoardState
from defs import NAME, ENGINE_VERSION, ENGINE_STATUS, preset_positions
from time import perf_counter
import evaluation

get_time_ms = lambda i : round(i * 1000)

if __name__ == '__main__':
    print(f'\n  [STARTING UP {NAME}]')
    print(f'  [RUNNING ON]: {sys.version}')
    print(f'  [ENGINE VERSION]: {ENGINE_VERSION}')
    print(f'  [ENGINE DEVELOPMENT STATUS]: {ENGINE_STATUS}')

    # init board and parse FEN
    board: BoardState = BoardState()
    start_time: float = perf_counter()
    board.init_state(preset_positions['tricky_position'])
    board.print_board()

    # call perft test
    board.perft_test(3)

    # debugging evaluation function
    print(f'  [EVALUATION (HANDCRAFTED)]: {evaluation.evaluate(board.board, board.side, board.pce_count, board.hash_key)}')

    # calc program runtime
    program_runtime: float = perf_counter() - start_time

    # print program runtime
    print(f'\n  [PROGRAM FINISHED IN {get_time_ms(program_runtime)} ms, {program_runtime} sec]')
