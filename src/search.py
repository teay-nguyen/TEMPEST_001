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
from transposition import Transposition, HASH_ALPHA, HASH_BETA, HASH_EXACT, NO_HASH_ENTRY
from evaluation import evaluate
from board0x88 import MovesStruct
from time import perf_counter
from defs import CAPTURE_MOVES, ALL_MOVES, IDS, PIECE_TYPES, get_move_capture, get_move_source,\
                 BSQUARES, get_move_target, _print, print_move

# definitions
INF:int = int(1e8)
M_VAL:int = 100000
M_SCORE:int = 99000
MAX_PLY:int = 4**3
TO_MS = lambda _t: round(_t * 1000)
GET_CURR_MS = lambda: TO_MS(perf_counter())

# some defaults
_DEFAULT_TIMELIMIT:int = 20
_DEFAULT_SEARCHDEPTH:int = 6

MVV_LVA:tuple = ( # mvv lva table, most valuable victim - least valuable attacker
    0,   0,   0,   0,   0,   0,   0,  0,   0,   0,   0,   0,   0,
    0, 105, 205, 305, 405, 505, 605,  105, 205, 305, 405, 505, 605,
    0, 104, 204, 304, 404, 504, 604,  104, 204, 304, 404, 504, 604,
    0, 103, 203, 303, 403, 503, 603,  103, 203, 303, 403, 503, 603,
    0, 102, 202, 302, 402, 502, 602,  102, 202, 302, 402, 502, 602,
    0, 101, 201, 301, 401, 501, 601,  101, 201, 301, 401, 501, 601,
    0, 100, 200, 300, 400, 500, 600,  100, 200, 300, 400, 500, 600,

    0, 105, 205, 305, 405, 505, 605,  105, 205, 305, 405, 505, 605,
    0, 104, 204, 304, 404, 504, 604,  104, 204, 304, 404, 504, 604,
    0, 103, 203, 303, 403, 503, 603,  103, 203, 303, 403, 503, 603,
    0, 102, 202, 302, 402, 502, 602,  102, 202, 302, 402, 502, 602,
    0, 101, 201, 301, 401, 501, 601,  101, 201, 301, 401, 501, 601,
    0, 100, 200, 300, 400, 500, 600,  100, 200, 300, 400, 500, 600,
)

class standard_searcher:
    def __init__(self) -> None:
        self._km:list = [[0 for _ in range(MAX_PLY)] for _ in range(IDS)]
        self._hm:list = [[0 for _ in range(BSQUARES)] for _ in range(PIECE_TYPES)]
        self._pv:list = [[0 for _ in range(MAX_PLY)] for _ in range(MAX_PLY)]
        self._pvlength:list = [0 for _ in range(MAX_PLY)]
        self._ply, self._nodes, self._tt_base, self._tbhits = 0, 0, Transposition(), 0
        self._time_utils:dict = {'abort':0, 'start_t':0, 'end_t':0, 'max_t':0, 'is_set':0}

        self._follow_pv:int = 0
        self._score_pv:int = 0
        self._enabled:int = 1

        self._clear_vals()
        self._clear_tbls()
        self._clear_time_utils()
        self._clear_tt() 

    def _clear_tbls(self) -> None:
        self._km:list = [[0 for _ in range(MAX_PLY)] for _ in range(IDS)]
        self._hm:list = [[0 for _ in range(BSQUARES)] for _ in range(PIECE_TYPES)]
        self._pv:list = [[0 for _ in range(MAX_PLY)] for _ in range(MAX_PLY)]
        self._pvlength:list = [0 for _ in range(MAX_PLY)]

    def _clear_vals(self) -> None: self._ply, self._nodes, self._follow_pv, self._score_pv, self._tbhits = 0, 0, 0, 0, 0
    def _clear_time_utils(self) -> None: self._time_utils:dict = {'abort':0, 'start_t':0, 'end_t':0, 'max_t':0, 'is_set':0}
    def _clear_tt(self) -> None: self._tt_base.tt_setsize(0xCCCCC)

    def _clear_all(self) -> None:
        self._clear_vals()
        self._clear_tbls()
        self._clear_time_utils()
        self._clear_tt()

    def _init_timer(self, _allocated:int = _DEFAULT_TIMELIMIT) -> None:
        self._time_utils['start_t'] = GET_CURR_MS()
        self._time_utils['max_t'] = TO_MS(_allocated)
        self._time_utils['end_t'] = self._time_utils['start_t'] + self._time_utils['max_t']
        self._time_utils['is_set'] = 1

    def _checkup(self) -> None:
        curr_time:int = GET_CURR_MS(); elapsed:int = curr_time - self._time_utils['start_t']
        if curr_time >= self._time_utils['end_t']: _print(f'time limit exceeded: {elapsed} ms\n'); self._time_utils['abort'] = 1

    def _enable_pv_scoring(self, m_list:MovesStruct):
        self._follow_pv:int = 0
        for c in range(m_list.count):
            if self._pv[0][self._ply] == m_list.moves[c].move: self._score_pv = 1; self._follow_pv = 1

    def _score_move(self, board:list, move:int) -> int:
        if self._score_pv and self._pv[0][self._ply] == move: self._score_pv = 0; return 20000
        if get_move_capture(move): return MVV_LVA[board[get_move_source(move)] * 13 + board[get_move_target(move)]] + 10000
        else:
            if self._km[0][self._ply] == move: return 9000
            elif self._km[1][self._ply] == move: return 8000
            else: return self._hm[board[get_move_source(move)]][get_move_target(move)]

    def _sort_moves(self, board:list, move_list:MovesStruct) -> None:
        for c in range(move_list.count): move_list.moves[c].score = self._score_move(board, move_list.moves[c].move)
        move_list.moves.sort(reverse=True,key=lambda x:x.score)

    def _is_rep(self, pos) -> int:
        assert hasattr(pos, 'board') and hasattr(pos, 'hash_key')
        return pos.hash_key in pos.reps

    def _is_mate(self, score:int) -> int: return abs(score) > M_SCORE
    def _to_mate(self, score:int) -> int: return M_VAL - abs(score)

    def _quiesce(self, alpha:int, beta:int, pos) -> int:
        if not (self._nodes & 2047): self._checkup()
        if self._time_utils['abort']: return 0
        self._nodes += 1
        if self._ply > MAX_PLY - 1: return evaluate(pos.board, pos.side, pos.pce_count, pos.hash_key, pos.fifty)
        stand_pat:int = evaluate(pos.board, pos.side, pos.pce_count, pos.hash_key, pos.fifty)
        if stand_pat >= beta: return beta
        if stand_pat > alpha: alpha = stand_pat

        m_list:MovesStruct = MovesStruct()
        pos.gen_moves(m_list); self._sort_moves(pos.board, m_list)

        for c in range(m_list.count):
            board_cpy:list = [_ for _ in pos.board]
            side_cpy:int = pos.side
            xside_cpy:int = pos.xside
            enpassant_cpy:int = pos.enpassant
            castle_cpy:int = pos.castle
            king_square_cpy:list = [_ for _ in pos.king_square]
            pce_count_cpy:list = [_ for _ in pos.pce_count]
            hashkey_cpy:int = pos.hash_key
            fifty_cpy:int = pos.fifty
            reps_cpy:list = [_ for _ in pos.reps]

            self._ply += 1

            if not pos.make_move(m_list.moves[c].move, CAPTURE_MOVES, searching = 1):
                self._ply -= 1; continue

            score:int = -self._quiesce(-beta, -alpha, pos)

            self._ply -= 1

            pos.board = [_ for _ in board_cpy]
            pos.side = side_cpy
            pos.xside = xside_cpy
            pos.enpassant = enpassant_cpy
            pos.castle = castle_cpy
            pos.king_square = [_ for _ in king_square_cpy]
            pos.pce_count = [_ for _ in pce_count_cpy]
            pos.hash_key = hashkey_cpy
            pos.fifty = fifty_cpy
            pos.reps = [_ for _ in reps_cpy]

            if self._time_utils['abort']: return 0

            if score > alpha:
                alpha = score
                if score >= beta:
                    return beta

        return alpha

    def _ab(self, alpha:int, beta:int, depth:int, pos) -> int:
        self._pvlength[self._ply] = self._ply
        score:int = 0; _hash_flag:int = HASH_ALPHA; pv_node:int = beta - alpha > 1
        if self._ply and self._is_rep(pos) or pos.fifty >= 100: return 0
        score = self._tt_base.tt_probe(depth, alpha, beta, pos.hash_key, self._ply)
        if self._ply and score != NO_HASH_ENTRY and not pv_node: self._tbhits += 1; return score
        if not (self._nodes & 2047): self._checkup()
        if self._time_utils['abort']: return 0
        if not depth: return self._quiesce(alpha, beta, pos)
        if self._ply > MAX_PLY - 1: return evaluate(pos.board, pos.side, pos.pce_count, pos.hash_key, pos.fifty)
        self._nodes += 1; in_check:int = pos.in_check(pos.side)
        if in_check: depth += 1
        is_legal:int = 0

        m_list:MovesStruct = MovesStruct()
        pos.gen_moves(m_list)
        if self._follow_pv: self._enable_pv_scoring(m_list)
        self._sort_moves(pos.board, m_list)

        for c in range(m_list.count):
            board_cpy:list = [_ for _ in pos.board]
            side_cpy:int = pos.side
            xside_cpy:int = pos.xside
            enpassant_cpy:int = pos.enpassant
            castle_cpy:int = pos.castle
            king_square_cpy:list = [_ for _ in pos.king_square]
            pce_count_cpy:list = [_ for _ in pos.pce_count]
            hashkey_cpy:int = pos.hash_key
            fifty_cpy:int = pos.fifty
            reps_cpy:list = [_ for _ in pos.reps]

            self._ply += 1

            if not pos.make_move(m_list.moves[c].move, ALL_MOVES, searching = 1):
                self._ply -= 1; continue

            is_legal:int = 1

            score:int = -self._ab(-beta, -alpha, depth - 1, pos)

            self._ply -= 1

            pos.board = [_ for _ in board_cpy]
            pos.side = side_cpy
            pos.xside = xside_cpy
            pos.enpassant = enpassant_cpy
            pos.castle = castle_cpy
            pos.king_square = [_ for _ in king_square_cpy]
            pos.pce_count = [_ for _ in pce_count_cpy]
            pos.hash_key = hashkey_cpy
            pos.fifty = fifty_cpy
            pos.reps = [_ for _ in reps_cpy]

            if self._time_utils['abort']: return 0

            if score > alpha:
                _hash_flag:int = HASH_EXACT; alpha = score
                if not get_move_capture(m_list.moves[c].move): self._hm[pos.board[get_move_source(m_list.moves[c].move)]][get_move_target(m_list.moves[c].move)] += depth
                self._pv[self._ply][self._ply] = m_list.moves[c].move
                for next_ply in range(self._ply + 1, self._pvlength[self._ply + 1]): self._pv[self._ply][next_ply] = self._pv[self._ply + 1][next_ply]
                self._pvlength[self._ply] = self._pvlength[self._ply + 1]
                if score >= beta:
                    self._tt_base.tt_save(depth, beta, HASH_BETA, pos.hash_key, self._ply)
                    if not get_move_capture(m_list.moves[c].move):
                        self._km[1][self._ply] = self._km[0][self._ply]
                        self._km[0][self._ply] = m_list.moves[c].move
                    return beta
        if not is_legal:
            if in_check: return -M_VAL + self._ply
            else: return 0

        self._tt_base.tt_save(depth, alpha, _hash_flag, pos.hash_key, self._ply)
        return alpha

    def _start_search(self, pos, _depth = _DEFAULT_SEARCHDEPTH, _allocated = _DEFAULT_TIMELIMIT) -> int:
        self._clear_all()
        if not self._enabled: _print(f'\nsearcher not available for use, enabled: {self._enabled}\n'); return 0
        self._init_timer(_allocated)
        alpha:int = -INF; beta:int = INF; score:int = 0
        for _k, _v in self._time_utils.items(): _print(f'{_k}: {_v} ')
        _print('\n')
        for c_d in range(1, _depth + 1):
            score:int = self._ab(alpha, beta, c_d, pos)
            elapsed:int = GET_CURR_MS() - self._time_utils['start_t']
            if not elapsed: elapsed += 1
            if self._time_utils['abort']: _print('search aborted!\n'); break
            if self._pvlength[0]:
                if score > -M_VAL and score < -M_SCORE: _print(f'info depth {c_d} nodes {self._nodes} mate {abs(-(score+M_VAL)//2-1)} nps {TO_MS(self._nodes)//elapsed} tbhits {self._tbhits} time {elapsed} pv ')
                elif score > M_SCORE and score < M_VAL: _print(f'info depth {c_d} nodes {self._nodes} mate {(M_VAL-score)//2+1} nps {TO_MS(self._nodes)//elapsed} tbhits {self._tbhits} time {elapsed} pv ')
                else: _print(f'info depth {c_d} nodes {self._nodes} cp {score} nps {TO_MS(self._nodes)//elapsed} tbhits {self._tbhits} time {elapsed} pv ')
                for _m in range(self._pvlength[0]): print_move(self._pv[0][_m])
                if self._enabled: _print('\n')
            else: _print(f'info depth 0 mate 0  {"white" if pos.side^1 else "black"} wins\n'); self._enabled = 0; print(f'searcher is now locked, enabled: {self._enabled}'); return 0
        _print('\n')
        if self._pv[0][0]:
            _print('bestmove ')
            print_move(self._pv[0][0], '\n')
        else: print('bestmove n/a')
        return 1
