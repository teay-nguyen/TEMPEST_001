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
from defs import IDS, BSQUARES, PIECE_TYPES, get_move_source, get_move_target,\
                get_move_capture, ALL_MOVES, CAPTURE_MOVES, print_move

from board0x88 import MovesStruct
from evaluation import evaluate
from time import perf_counter
from transposition import Transposition, NO_HASH_ENTRY, HASH_ALPHA, HASH_BETA, HASH_EXACT

# define prerequisite variables
mvv_lva:list = [

    [0,   0,   0,   0,   0,   0,   0,     0,   0,   0,   0,   0,   0],
    [0, 105, 205, 305, 405, 505, 605,   105, 205, 305, 405, 505, 605],
    [0, 104, 204, 304, 404, 504, 604,   104, 204, 304, 404, 504, 604],
    [0, 103, 203, 303, 403, 503, 603,   103, 203, 303, 403, 503, 603],
    [0, 102, 202, 302, 402, 502, 602,   102, 202, 302, 402, 502, 602],
    [0, 101, 201, 301, 401, 501, 601,   101, 201, 301, 401, 501, 601],
    [0, 100, 200, 300, 400, 500, 600,   100, 200, 300, 400, 500, 600],

    [0, 105, 205, 305, 405, 505, 605,   105, 205, 305, 405, 505, 605],
    [0, 104, 204, 304, 404, 504, 604,   104, 204, 304, 404, 504, 604],
    [0, 103, 203, 303, 403, 503, 603,   103, 203, 303, 403, 503, 603],
    [0, 102, 202, 302, 402, 502, 602,   102, 202, 302, 402, 502, 602],
    [0, 101, 201, 301, 401, 501, 601,   101, 201, 301, 401, 501, 601],
    [0, 100, 200, 300, 400, 500, 600,   100, 200, 300, 400, 500, 600],

]

POS_INF = 99999
NEG_INF = -99999
MATE_VAL = 49000
MAX_PLY = 64

tt = Transposition()
tt.tt_setsize(0xCCCCC)

get_ms = lambda t:round(t * 1000)

# standard searcher for TEMPEST_001, utilizing alphabeta
# other search methods like MTD(f) or NegaScout are to be explored later

class _standard():
    def __init__(self) -> None:
        self.timing_util = {'starttime':0, 'stoptime':0, 'abort':0, 'limit':get_ms(9), 'timeset':0}

        self.killer_moves = [[0 for _ in range(MAX_PLY)] for _ in range(IDS)]
        self.history_moves = [[0 for _ in range(BSQUARES)] for _ in range(PIECE_TYPES)]
        self.pv_table = [[0 for _ in range(MAX_PLY)] for _ in range(MAX_PLY)]
        self.pv_length = [0 for _ in range(MAX_PLY)]

        self.ply = 0
        self.nodes = 0

    def _reset_timecontrol(self) -> None:
        self.timing_util = {'starttime':0, 'stoptime':0, 'abort':0, 'limit':get_ms(9), 'timeset':0}

    def _start_timecontrol(self) -> None:
        self.timing_util['starttime'] = get_ms(perf_counter())
        self.timing_util['stoptime'] = self.timing_util['starttime'] + self.timing_util['limit']
        self.timing_util['timeset'] = 1

    def _clear(self) -> None:
        self.nodes = 0
        self.ply = 0
        self.timing_util['abort'] = 0

        self.killer_moves = [[0 for _ in range(MAX_PLY)] for _ in range(IDS)]
        self.history_moves = [[0 for _ in range(BSQUARES)] for _ in range(PIECE_TYPES)]
        self.pv_table = [[0 for _ in range(MAX_PLY)] for _ in range(MAX_PLY)]
        self.pv_length = [0 for _ in range(MAX_PLY)]

    def _checkup(self) -> None:
        if self.timing_util['timeset'] and (get_ms(perf_counter()) > self.timing_util['stoptime']): self.timing_util['abort'] = 1

    def _score(self, board:list, move:int) -> int:
        if self.pv_table[0][self.ply] == move: return 20000
        score:int = mvv_lva[board[get_move_source(move)]][board[get_move_target(move)]]
        if get_move_capture(move): score += 10000
        else:
            if self.killer_moves[0][self.ply] == move: return 9000
            elif self.killer_moves[1][self.ply] == move: return 8000
            else: return self.history_moves[board[get_move_source(move)]][get_move_target(move)] + 7000
        return score

    def _sort(self, board:list, move_list:MovesStruct) -> None:
        for c in range(move_list.count): move_list.moves[c].score = self._score(board, move_list.moves[c].move)
        move_list.moves.sort(reverse=True, key=lambda x:x.score)

    def _root(self, pos, depth:int = 5) -> None:
        self._clear()
        self._reset_timecontrol()
        self._start_timecontrol()

        score:int = 0
        self.nodes:int = 0

        print()
        for c_d in range(1, depth+1):
            score = self._alphabeta(NEG_INF, POS_INF, c_d, pos)
            if score <= -MATE_VAL or score >= MATE_VAL-1: print('  mate found!'); break
            if self.timing_util['abort']: break
            print(f'  info score cp {score} depth {c_d} nodes {self.nodes} pv', end=' ')
            for _m in range(self.pv_length[0]): print_move(self.pv_table[0][_m])
            print()

        print('', end='  ')
        if self.pv_table[0][0]: print_move(self.pv_table[0][0])
        else: print('n/a', end=' ')
        print('is the best move\n')

        if self.pv_table[0][0]: pos.make_move(self.pv_table[0][0], ALL_MOVES)
        else: print('  no move found!')
        pos.print_board()

    def _quiesce(self, alpha:int, beta:int, pos) -> int:
        assert beta > alpha
        self.nodes += 1

        if (self.nodes & 2047) == 0:
            self._checkup()
            if self.timing_util['abort']: return 0

        self.pv_length[self.ply] = self.ply

        if self.ply > (MAX_PLY-1): return beta

        threshold = evaluate(pos.board, pos.side, pos.pce_count, pos.hash_key, pos.fifty)
        if threshold > alpha:
            if threshold >= beta:
                return threshold
            alpha = threshold

        move_list = MovesStruct()
        pos.gen_moves(move_list)
        self._sort(pos.board, move_list)

        for c in range(move_list.count):
            board_cpy:list = [_ for _ in pos.board]
            side_cpy:int = pos.side
            xside_cpy:int = pos.xside
            enpassant_cpy:int = pos.enpassant
            castle_cpy:int = pos.castle
            king_square_cpy:list = [_ for _ in pos.king_square]
            pce_count_cpy:list = [_ for _ in pos.pce_count]
            hashkey_cpy:int = pos.hash_key
            fifty_cpy:int = pos.fifty

            self.ply += 1

            if not pos.make_move(move_list.moves[c].move, CAPTURE_MOVES):
                self.ply -= 1
                continue

            score = -self._quiesce(-beta, -alpha, pos)

            pos.board = [_ for _ in board_cpy]
            pos.side = side_cpy
            pos.xside = xside_cpy
            pos.enpassant = enpassant_cpy
            pos.castle = castle_cpy
            pos.king_square = [_ for _ in king_square_cpy]
            pos.pce_count = [_ for _ in pce_count_cpy]
            pos.hash_key = hashkey_cpy
            pos.fifty = fifty_cpy

            self.ply -= 1

            if self.timing_util['abort']: return 0

            if score > alpha:
                if score >= beta:
                    return beta
                alpha = score
        return alpha

    def _alphabeta(self, alpha:int, beta:int, depth:int, pos) -> int:

        assert depth >= 0
        assert beta > alpha

        legal_:int = 0
        pv_node:int = beta - alpha > 1
        hash_flag:int = HASH_ALPHA
        b_search_pv:int = 1
        if self.ply and pos.fifty >= 100: return 0
        if depth <= 0: return self._quiesce(alpha, beta, pos)
        self.nodes += 1

        if (self.nodes & 2047) == 0:
            self._checkup()
            if self.timing_util['abort']: return 0

        if self.ply > MAX_PLY-1: return beta

        alpha = max(alpha, -MATE_VAL+self.ply-1)
        beta = min(beta, MATE_VAL-self.ply)
        if alpha >= beta: return alpha

        score:int = tt.tt_probe(depth, alpha, beta, pos.hash_key)
        if self.ply and score != NO_HASH_ENTRY and not pv_node: return score

        self.pv_length[self.ply] = self.ply
        in_check:int = pos.in_check(pos.side)
        if in_check: depth += 1

        move_list:MovesStruct = MovesStruct()
        pos.gen_moves(move_list)
        self._sort(pos.board, move_list)

        for c in range(move_list.count):
            board_cpy:list = [_ for _ in pos.board]
            side_cpy:int = pos.side
            xside_cpy:int = pos.xside
            enpassant_cpy:int = pos.enpassant
            castle_cpy:int = pos.castle
            king_square_cpy:list = [_ for _ in pos.king_square]
            pce_count_cpy:list = [_ for _ in pos.pce_count]
            hashkey_cpy:int = pos.hash_key
            fifty_cpy:int = pos.fifty

            self.ply += 1

            if not pos.make_move(move_list.moves[c].move, ALL_MOVES):
                self.ply -= 1
                continue

            legal_ += 1

            if b_search_pv:
                score = -self._alphabeta(-beta, -alpha, depth - 1, pos)
            else:
                score = -self._alphabeta(-alpha-1, -alpha, depth - 1, pos)
                if score > alpha and score < beta: score = -self._alphabeta(-beta, -alpha, depth - 1, pos)

            pos.board = [_ for _ in board_cpy]
            pos.side = side_cpy
            pos.xside = xside_cpy
            pos.enpassant = enpassant_cpy
            pos.castle = castle_cpy
            pos.king_square = [_ for _ in king_square_cpy]
            pos.pce_count = [_ for _ in pce_count_cpy]
            pos.hash_key = hashkey_cpy
            pos.fifty = fifty_cpy

            self.ply -= 1

            if self.timing_util['abort']: return 0

            if score >= beta:
                tt.tt_save(depth, beta, HASH_BETA, pos.hash_key)
                if not get_move_capture(move_list.moves[c].move):
                    self.killer_moves[1][self.ply] = self.killer_moves[0][self.ply]
                    self.killer_moves[0][self.ply] = move_list.moves[c].move
                return beta
            if score > alpha:
                hash_flag = HASH_EXACT
                alpha = score
                if not get_move_capture(move_list.moves[c].move): self.history_moves[pos.board[get_move_source(move_list.moves[c].move)]][get_move_target(move_list.moves[c].move)] += depth
                self.pv_table[self.ply][self.ply] = move_list.moves[c].move
                for _i in range(self.ply+1, self.pv_length[self.ply+1]): self.pv_table[self.ply][_i] = self.pv_table[self.ply+1][_i]
                self.pv_length[self.ply] = self.pv_length[self.ply+1]

        if not legal_:
            if in_check: return -MATE_VAL + self.ply
            else: return 0

        tt.tt_save(depth, alpha, hash_flag, pos.hash_key)
        return alpha
