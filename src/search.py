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
from __future__ import print_function, division
from defs import IDS, BSQUARES, PIECE_TYPES, get_move_source,\
                get_move_target, get_move_capture, get_move_promoted, ALL_MOVES,\
                CAPTURE_MOVES, print_move, K, k, P, N, R, FULL_DEPTH_MOVES, REDUCTION_LIMIT,\
                R_LIMIT

from board0x88 import MovesStruct
from evaluation import evaluate
from time import perf_counter
from transposition import Transposition, NO_HASH_ENTRY, HASH_ALPHA, HASH_BETA, HASH_EXACT
from data import piece_val

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

POS_INF:int = int(1e8)
NEG_INF:int = int(-1e8)
MATE_VAL:int = 50000
MATE_SCORE:int = 49000
MAX_PLY:int = 5**3
OPTIMAL_DEPTH:int = 6
TIME_LIMIT_FOR_SEARCH:int = 30
OFFBOARD:int = 120
OPENING_INDEX:int = 0
ENDGAME_INDEX:int = 1

DO_NULL:int = 1
NO_NULL:int = 0

get_ms = lambda t:round(t*1000)

# standard searcher for TEMPEST_001, utilizing alphabeta
# other search methods like MTD(f) or NegaScout are to be explored later

class _standard():
    def __init__(self) -> None:
        self._search_limitations:dict = {'inf_time_search':0}
        self._search_depth_from_input:int = 0
        self._search_time_allocation_from_input:int = 0
        self.timing_util:dict = { 'starttime':0, 'stoptime':0, 'abort':0, 'limit':get_ms(self._search_time_allocation_from_input), 'timeset':0 }
        self.tt_probing_base:Transposition = Transposition(); self.tt_probing_base.tt_setsize(0xCCCCC)

        self.killer_moves:list = [[0 for _ in range(MAX_PLY)] for _ in range(IDS)]
        self.history_moves:list = [[0 for _ in range(BSQUARES)] for _ in range(PIECE_TYPES)]
        self.pv_table:list = [[0 for _ in range(MAX_PLY)] for _ in range(MAX_PLY)]
        self.pv_length:list = [0 for _ in range(MAX_PLY)]

        self.ply:int = 0
        self.nodes:int = 0
        self.tb_hits:int = 0
        self.enabled:int = 1
        self.tt_reset_each_root:int = 1

    def _determine_search_limitations(self):
        if self._search_limitations['inf_time_search']: self.timing_util['limit'] = get_ms(POS_INF)
        else:
            if not self._search_time_allocation_from_input: self.timing_util['limit'] = get_ms(TIME_LIMIT_FOR_SEARCH)
            else: self.timing_util['limit'] = get_ms(self._search_time_allocation_from_input)

    def _reset_timecontrol(self) -> None:
        self.timing_util:dict = {'starttime':0, 'stoptime':0, 'abort':0, 'limit':get_ms(self._search_time_allocation_from_input), 'timeset':0}

    def _start_timecontrol(self) -> None:
        self.timing_util['starttime'] = get_ms(perf_counter())
        self.timing_util['stoptime'] = self.timing_util['starttime'] + self.timing_util['limit']
        self.timing_util['timeset'] = 1
        self.timing_util['abort'] = 0

    def _clear_search_tables(self) -> None:
        self.killer_moves:list = [[0 for _ in range(MAX_PLY)] for _ in range(IDS)]
        self.history_moves:list = [[0 for _ in range(BSQUARES)] for _ in range(PIECE_TYPES)]
        self.pv_table:list = [[0 for _ in range(MAX_PLY)] for _ in range(MAX_PLY)]
        self.pv_length:list = [0 for _ in range(MAX_PLY)]

    def _clear(self) -> None:
        self.nodes:int = 0
        self.ply:int = 0
        self.tb_hits:int = 0
        self.timing_util['abort'] = 0
        self._search_depth_from_input:int = 0
        self._search_time_allocation_from_input:int = 0
        self.tt_reset_each_root:int = 1
        self.tt_probing_base.tt_setsize(0xCCCCC)
        self._reset_timecontrol()
        self._clear_search_tables()

    def _matescore(self, score:int) -> int: return abs(score) > MATE_SCORE
    def _tomate(self, score:int) -> int: return MATE_VAL - abs(score)

    def _checkup(self) -> None:
        curr_time:int = get_ms(perf_counter())
        if self.timing_util['timeset'] and (curr_time >= self.timing_util['stoptime']):
            self.timing_util['abort'] = 1
            print(f'time limit exceeded! {curr_time - self.timing_util["starttime"]} ms')

    def _score(self, board:list, move:int) -> int:
        if self.pv_table[0][self.ply] == move: return 20000
        if get_move_capture(move): return 10000 + mvv_lva[board[get_move_source(move)]][board[get_move_target(move)]]
        else:
            if self.killer_moves[0][self.ply] == move: return 9000
            elif self.killer_moves[1][self.ply] == move: return 8000
            else: return self.history_moves[board[get_move_source(move)]][get_move_target(move)] + 7000

    def _sort(self, board:list, move_list:MovesStruct) -> None:
        for c in range(move_list.count): move_list.moves[c].score = self._score(board, move_list.moves[c].move)
        move_list.moves.sort(reverse=True, key=lambda x:x.score)

    def _root(self, pos, depth:int = OPTIMAL_DEPTH, _timeAllocated:int = TIME_LIMIT_FOR_SEARCH, _reset_tt:int = 1) -> int:
        self._clear()
        self._search_depth_from_input:int = depth
        self._search_time_allocation_from_input:int = _timeAllocated
        self.tt_reset_each_root:int = _reset_tt
        self._determine_search_limitations()
        self._start_timecontrol()
        if self.tt_reset_each_root: self.tt_probing_base.tt_setsize(0xCCCCC)
        if not self.enabled: print(f'\nsearcher not available for use, enabled: {self.enabled}', end='\n'); return 0
        score:int = 0; absolute_draw:int = 1

        print('\n', end='')
        for _k, _v in self.timing_util.items(): print(f'{_k}: {_v}', end=' ');
        print('\n', end='')
        for c_d in range(1, self._search_depth_from_input + 1):
            score:int = self._alphabeta(NEG_INF, POS_INF, c_d, pos, DO_NULL)
            elapsed:int = get_ms(perf_counter()) - self.timing_util['starttime']
            if not elapsed: elapsed += 1
            if self.timing_util['abort']: print('time limit exceeded for search!'); break
            if self.pv_length[0]:
                if score > -MATE_VAL and score < -MATE_SCORE: print(f'info depth {c_d} nodes {self.nodes} mate {abs(-(score+MATE_VAL)//2-1)} nps {get_ms(self.nodes)//elapsed} tbhits {self.tb_hits} time {elapsed} pv', end=' ')
                elif score > MATE_SCORE and score < MATE_VAL: print(f'info depth {c_d} nodes {self.nodes} mate {(MATE_VAL-score)//2+1} nps {get_ms(self.nodes)//elapsed} tbhits {self.tb_hits} time {elapsed} pv', end=' ')
                else: print(f'info depth {c_d} nodes {self.nodes} score {score} nps {get_ms(self.nodes)//elapsed} tbhits {self.tb_hits} time {elapsed} pv', end=' ')
                for _m in range(self.pv_length[0]): print_move(self.pv_table[0][_m])
                if self.enabled: print('', end='\n')
                for _v in range(len(pos.pce_count)):
                    if not _v or _v == K or _v == k: continue
                    if pos.pce_count[_v]: absolute_draw = 0
                if absolute_draw: self.enabled = 0; print('\n  GAME DRAWN!'); break
            else: print(f'info depth 0 mate 0   {"white" if pos.side ^ 1 else "black"} wins\n', end=''); self.enabled = 0; print(f'searcher is now locked, enabled: {self.enabled}'); return 0
        print('\n', end='')
        if self.pv_table[0][0]:
            print('bestmove', end=' ')
            print_move(self.pv_table[0][0], '\n')
            pos.make_move(self.pv_table[0][0], ALL_MOVES, searching=0)
            pos.print_board(); return 1
        else: print('bestmove n/a')
        return 1

    def _quiesce(self, alpha:int, beta:int, pos) -> int:
        assert beta > alpha
        self.nodes += 1
        self.pv_length[self.ply] = self.ply

        if not (self.nodes & 2047): self._checkup()
        if self.timing_util['abort']: print('time limit exceeded for search!'); return 0

        if self.ply > MAX_PLY - 1: return evaluate(pos.board, pos.side, pos.pce_count, pos.hash_key, pos.fifty)

        threshold = evaluate(pos.board, pos.side, pos.pce_count, pos.hash_key, pos.fifty)
        if threshold >= beta: return beta
        alpha = max(alpha, threshold)

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
            reps_cpy:list = [_ for _ in pos.reps]

            self.ply += 1

            if not pos.make_move(move_list.moves[c].move, CAPTURE_MOVES, searching=1):
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
            pos.reps = [_ for _ in reps_cpy]

            self.ply -= 1

            if self.timing_util['abort']: print('time limit exceeded for search!'); return 0

            if score > alpha:
                alpha = score
                self.pv_table[self.ply][self.ply] = move_list.moves[c].move
                for _i in range(self.ply+1, self.pv_length[self.ply+1]): self.pv_table[self.ply][_i] = self.pv_table[self.ply+1][_i]
                self.pv_length[self.ply] = self.pv_length[self.ply+1]
                if score >= beta: return beta
        return alpha

    def _alphabeta(self, alpha:int, beta:int, depth:int, pos, null_move:int) -> int:

        assert depth >= 0
        assert beta > alpha

        self.pv_length[self.ply] = self.ply

        legal_:int = 0
        score:int = 0
        pv_node:int = beta - alpha > 1
        hash_flag:int = HASH_ALPHA
        futility_pruning:int = 0
        if self.ply > 1 and (pos.hash_key in pos.reps): return 0
        score:int = self.tt_probing_base.tt_probe(depth, alpha, beta, pos.hash_key, self.ply)
        if self.ply and score != NO_HASH_ENTRY and not pv_node: self.tb_hits += 1; return score
        if not (self.nodes & 2047): self._checkup()
        if self.timing_util['abort']: print('time limit exceeded for search!'); return 0
        if not depth: return self._quiesce(alpha, beta, pos)
        if self.ply > 1 and pos.fifty >= 100: return 0
        if self.ply > MAX_PLY - 1: return evaluate(pos.board, pos.side, pos.pce_count, pos.hash_key, pos.fifty)
        self.nodes += 1
        if alpha < -MATE_VAL: alpha = -MATE_VAL
        if beta > MATE_VAL - 1: beta = MATE_VAL - 1
        if alpha >= beta: return alpha
        in_check:int = pos.in_check(pos.side)
        if in_check: depth += 1
        if not in_check and not pv_node:
            static_eval:int = evaluate(pos.board, pos.side, pos.pce_count, pos.hash_key, pos.fifty)
            if depth < 3 and abs(beta - 1) > -MATE_VAL + 100:
                eval_margin:int = piece_val[OPENING_INDEX][P] * depth
                if static_eval - eval_margin >= beta: return static_eval - eval_margin
            if null_move:
                if self.ply and depth > 2 and static_eval >= beta:
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

                    self.ply += 1
                    pos.reps.append(pos.hash_key)

                    if pos.enpassant != OFFBOARD: pos.hash_key ^= pos.zobrist.ep[pos.enpassant]
                    pos.enpassant = OFFBOARD

                    pos.side ^= 1; pos.xside ^= 1
                    pos.hash_key ^= pos.zobrist.side

                    score:int = -self._alphabeta(-beta, -beta + 1, depth - 1 - R_LIMIT, pos, NO_NULL)

                    self.ply -= 1

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

                    if self.timing_util['abort']: print('time limit exceeded for search!'); return 0
                    if score >= beta: return beta

                score:int = static_eval + piece_val[OPENING_INDEX][P]; new_score:int = 0
                if score < beta:
                    if depth == 1:
                        new_score = self._quiesce(alpha, beta, pos)
                        return new_score if new_score > score else score
                score += piece_val[OPENING_INDEX][P]
                if score < beta and depth < 4:
                    new_score = self._quiesce(alpha, beta, pos)
                    if new_score < beta: return new_score if new_score > score else score
            futility_margin:list = [0, piece_val[OPENING_INDEX][P], piece_val[OPENING_INDEX][N], piece_val[OPENING_INDEX][R]]
            if depth < 4 and abs(alpha) < MATE_SCORE and static_eval + futility_margin[depth] <= alpha: futility_pruning = 1

        moves_searched:int = 0
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
            reps_cpy:list = [_ for _ in pos.reps]

            self.ply += 1

            if not pos.make_move(move_list.moves[c].move, ALL_MOVES, searching=1):
                self.ply -= 1
                continue

            legal_ = 1

            if (
                    futility_pruning and\
                    moves_searched and\
                    not get_move_capture(move_list.moves[c].move) and\
                    not get_move_promoted(move_list.moves[c].move) and\
                    not pos.is_square_attacked(pos.king_square[pos.side], pos.xside)
               ):
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
                    continue

            if not moves_searched: score = -self._alphabeta(-beta, -alpha, depth - 1, pos, DO_NULL)
            else:
                if  (
                     not pv_node and\
                     moves_searched >= FULL_DEPTH_MOVES and\
                     depth >= REDUCTION_LIMIT and\
                     not in_check and\
                     not get_move_capture(move_list.moves[c].move) and\
                     not get_move_promoted(move_list.moves[c].move)
                    ): score:int = -self._alphabeta(-alpha - 1, -alpha, depth - 2, pos, DO_NULL)
                else: score:int = alpha + 1
                if score > alpha:
                    score:int = -self._alphabeta(-alpha - 1, -alpha, depth - 1, pos, DO_NULL)
                    if alpha < score < beta: score:int = -self._alphabeta(-beta, -alpha, depth - 1, pos, DO_NULL)

            self.ply -= 1

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

            if self.timing_util['abort']: print('time limit exceeded for search!'); return 0
            moves_searched += 1

            if score > alpha:
                hash_flag = HASH_EXACT
                alpha = score
                if not get_move_capture(move_list.moves[c].move): self.history_moves[pos.board[get_move_source(move_list.moves[c].move)]][get_move_target(move_list.moves[c].move)] += depth
                self.pv_table[self.ply][self.ply] = move_list.moves[c].move
                for _i in range(self.ply+1, self.pv_length[self.ply+1]): self.pv_table[self.ply][_i] = self.pv_table[self.ply+1][_i]
                self.pv_length[self.ply] = self.pv_length[self.ply+1]
                if score >= beta:
                    self.tt_probing_base.tt_save(depth, beta, HASH_BETA, pos.hash_key, self.ply)
                    if not get_move_capture(move_list.moves[c].move):
                        self.killer_moves[1][self.ply] = self.killer_moves[0][self.ply]
                        self.killer_moves[0][self.ply] = move_list.moves[c].move
                    return beta

        if not legal_:
            if in_check: return -MATE_VAL + self.ply
            else: return 0

        self.tt_probing_base.tt_save(depth, alpha, hash_flag, pos.hash_key, self.ply)
        return alpha

if __name__ == "__main__":
    _ = _standard()
