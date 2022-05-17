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

# imports
from __future__ import print_function
import search
import board0x88
import evaluation
from defs import *

# parse move string and turn it into something the engine can understand
def parse_move(move_str:str, pos:board0x88.BoardState):
    move_list:board0x88.MovesStruct = board0x88.MovesStruct(); pos.gen_moves(move_list)
    parse_from:int = (ord(move_str[0]) - ord('a')) + (8 - (ord(move_str[1]) - ord('0'))) * 16
    parse_to:int = (ord(move_str[2]) - ord('a')) + (8 - (ord(move_str[3]) - ord('0'))) * 16
    promoted_piece:int = 0; move:int = 0
    for c in range(move_list.count):
        move:int = move_list.moves[c].move
        if get_move_source(move) == parse_from and get_move_target(move) == parse_to:
            promoted_piece:int = get_move_promoted(move)
            if promoted_piece:
                if (promoted_piece == N or promoted_piece == n) and move_str[4] == 'n': return move
                elif (promoted_piece == B or promoted_piece == b) and move_str[4] == 'b': return move
                elif (promoted_piece == R or promoted_piece == r) and move_str[4] == 'r': return move
                elif (promoted_piece == Q or promoted_piece == q) and move_str[4] == 'q': return move
                continue
            return move
    return 0

def uci_prompt():
    print("id name TEMPEST_001"); print("id author Terry Nguyen"); print('type "help" for commands'); print("uciok")
    board = board0x88.BoardState()
    board.init_state(preset_positions['start_position'])
    searcher = search._standard()

    try:
        while 1:
            try: _input:str = input()
            except: exit()
            if _input == '': continue
            elif _input == 'uci': print('id name TEMPEST_001'); print('id author Terry Nguyen'); print('uciok');
            elif _input == 'isready': print('readyok'); continue
            elif _input == 'ucinewgame': board.init_state(preset_positions['start_position']); searcher.tt_probing_base.tt_setsize(0xCCCCC)
            elif _input[:23] == 'position startpos moves':
                board.init_state(preset_positions['start_position']); board.print_board(); moves = _input[24:].split()
                if not len(moves): raise RuntimeError('calling position startpos moves with any moves')
                for move in moves:
                    if move != ' ': board.make_move(parse_move(move, board), ALL_MOVES)
            elif _input[:8] == 'go perft': board.perft_test(int(_input[9:]))
            elif _input == 'position startpos': board.init_state(preset_positions['start_position']); board.print_board()
            elif _input[:12] == 'position fen': fen_string:str = _input[13:]; board.init_state(fen_string)
            elif _input[:8] == 'go depth': search_depth:int = int(_input[9:]); searcher._root(board, depth=search_depth)
            elif _input == 'go': searcher._root(board, depth=6)
            elif _input == 'd': board.print_board()
            elif _input == 'eval': board.print_board(); print(f'\n  [EVALUATION (HANDCRAFTED)]: {evaluation.evaluate(board.board, board.side, board.pce_count, board.hash_key, board.fifty)}')
            elif _input == 'unlock searcher': searcher.enabled = 1; print('searcher unlocked')
            elif _input == 'lock searcher': searcher.enabled = 0; print('searcher locked')
            elif _input == 'help': print('\nucinewgame - start new game'); print('position startpos - loads the start position'); print('position fen (fen string) - load fen string into engine');\
                                    print('go depth (search depth) - search at specified depth'); print('go perft (depth) - perform the debug perft');\
                                    print('uci - engine info'); print('d - prints the board with properties'); print('eval - call the evaluation function');\
                                    print("unlock searcher - enable the searcher so it doesn't throw an error"); print("lock searcher - lock the searcher so it denies any calls to search");\
                                    print('quit - break out of engine loop')
            elif _input == 'quit' or _input == 'exit': break
            print('\n', end='')
    except: print(searcher.ply); exit()
