#!/usr/bin/env pypy3 -u
# -*- coding: utf-8 -*-

import sys
from board0x88 import BoardState
from defs import *
from time import perf_counter
from eval import evaluate

get_time_ms = lambda i:round(i * 1000)

if __name__ == '__main__':
    print(f'\n  [STARTING UP {NAME}]')
    print(f'  [RUNNING ON]: {sys.version}')
    print(f'  [ENGINE VERSION]: {ENGINE_VERSION}')
    print(f'  [ENGINE DEVELOPMENT STATUS]: {ENGINE_STATUS}')

    # init board and parse FEN
    board: BoardState = BoardState()
    start_time: float = perf_counter()
    board.init_state('r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R b KQkq - ')
    board.print_board()

    # print unique hash key
    print(f'\n  [UNIQUE HASHKEY]: {board.hash_key}')
    print(f'  [HANDCRAFTED STATIC EVAL]: {evaluate(board.board, board.side, board.pce_count, board.hash_key)}')

    # calc program runtime
    program_runtime: float = perf_counter() - start_time

    # print program runtime
    print(f'\n  [PROGRAM FINISHED IN {get_time_ms(program_runtime)} ms, {program_runtime} sec]')
