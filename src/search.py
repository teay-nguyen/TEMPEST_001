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
from data import INFINITE, MATE_SCORE, MATE_VALUE, MAX_PLY
from defs import IDS, BOARD_SQ_NUM, PIECE_TYPES, get_move_source, get_move_target, get_move_capture, ALL_MOVES, CAPTURE_MOVES, print_move
from board0x88 import MovesStruct
from evaluation import evaluate

# most valuable victim <- least valuable aggressor/attacker
MVV_LVA:tuple = (
    0,   0,   0,   0,   0,   0,   0,    0,   0,   0,   0,   0,   0,
    0, 105, 205, 305, 405, 505, 605,    105, 205, 305, 405, 505, 605,
    0, 104, 204, 304, 404, 504, 604,    104, 204, 304, 404, 504, 604,
    0, 103, 203, 303, 403, 503, 603,    103, 203, 303, 403, 503, 603,
    0, 102, 202, 302, 402, 502, 602,    102, 202, 302, 402, 502, 602,
    0, 101, 201, 301, 401, 501, 601,    101, 201, 301, 401, 501, 601,
    0, 100, 200, 300, 400, 500, 600,    100, 200, 300, 400, 500, 600,


    0, 105, 205, 305, 405, 505, 605,    105, 205, 305, 405, 505, 605,
    0, 104, 204, 304, 404, 504, 604,    104, 204, 304, 404, 504, 604,
    0, 103, 203, 303, 403, 503, 603,    103, 203, 303, 403, 503, 603,
    0, 102, 202, 302, 402, 502, 602,    102, 202, 302, 402, 502, 602,
    0, 101, 201, 301, 401, 501, 601,    101, 201, 301, 401, 501, 601,
    0, 100, 200, 300, 400, 500, 600,    100, 200, 300, 400, 500, 600,
)

# standard searcher for TEMPEST_001
# other search methods like MTD(f) or NegaScout are to be explored later
class _standard:
    def __init__(self):
        self.nodes:int = 0
        self.ply:int = 0
        self.killer_moves:list = [0 for _ in range(IDS * MAX_PLY)]
        self.history_moves:list = [0 for _ in range(PIECE_TYPES * BOARD_SQ_NUM)]
        self.pv_table:list = [0 for _ in range(MAX_PLY**2)]
        self.pv_length:list = [0 for _ in range(MAX_PLY)]

    def _root(self, depth:int, pos):
        pass

    def _score(self, board:list, move:int) -> int:
        return 0

    def _sort(self, board:list, move_list:MovesStruct) -> None:
        pass

    def _quiesce(self, alpha:int, beta:int, pos) -> int:
        return 0

    def _alphabeta(self, alpha:int, beta:int, depth:int, pos) -> int:
        return 0
