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
import search
import board0x88
import evaluation
from defs import *

# parse move string and turn it into something the engine can understand
def parse_move(move_str:str, pos:board0x88.BoardState):
    move_list:board0x88.MovesStruct = board0x88.MovesStruct()
    pos.gen_moves(move_list)
    parse_from:int = (ord(move_str[0]) - ord('a')) + (8 - (ord(move_str[1]) - ord('0'))) * 16
    parse_to:int = (ord(move_str[2]) - ord('a')) + (8 - (ord(move_str[3]) - ord('0'))) * 16
    promoted_piece:int = 0
    move:int = 0
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
