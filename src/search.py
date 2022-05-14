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
                get_move_capture, ALL_MOVES, CAPTURE_MOVES, print_move, squares

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

POS_INF:int = int(1e7)
NEG_INF:int = int(-1e7)
MATE_VAL:int = 49000
MAX_PLY:int = 60
OPTIMAL_DEPTH:int = 5
TIME_LIMIT_FOR_SEARCH:int = 25

tt = Transposition()
tt.tt_setsize(0xCCCCC)

get_ms = lambda t:round(t * 1000)

# standard searcher for TEMPEST_001, utilizing alphabeta
# other search methods like MTD(f) or NegaScout are to be explored later

class _standard():
    def __init__(self) -> None:
        self._search_limitations:dict = {'inf_time_search':0}
        self._search_depth_from_input:int = 0
        self._search_time_allocation_from_input:int = 0
        self.timing_util:dict = {'starttime':0, 'stoptime':0, 'abort':0, 'limit':get_ms(self._search_time_allocation_from_input), 'timeset':0}

        self.killer_moves:list = [[0 for _ in range(MAX_PLY)] for _ in range(IDS)]
        self.history_moves:list = [[0 for _ in range(BSQUARES)] for _ in range(PIECE_TYPES)]
        self.pv_table:list = [[0 for _ in range(MAX_PLY)] for _ in range(MAX_PLY)]
        self.pv_length:list = [0 for _ in range(MAX_PLY)]

        self.ply:int = 0
        self.nodes:int = 0
        self.tb_hits:int = 0
        self.enabled:int = 1

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
        self.killer_moves = [[0 for _ in range(MAX_PLY)] for _ in range(IDS)]
        self.history_moves = [[0 for _ in range(BSQUARES)] for _ in range(PIECE_TYPES)]
        self.pv_table = [[0 for _ in range(MAX_PLY)] for _ in range(MAX_PLY)]
        self.pv_length = [0 for _ in range(MAX_PLY)]

    def _clear(self) -> None:
        self.nodes = 0
        self.ply = 0
        self.tb_hits = 0
        self.timing_util['abort'] = 0
        self._search_depth_from_input = 0
        self._search_time_allocation_from_input = 0
        self._reset_timecontrol()
        self._clear_search_tables()

    def _checkup(self) -> None:
        curr_time:int = get_ms(perf_counter())
        if self.timing_util['timeset'] and (curr_time >= self.timing_util['stoptime']):
            self.timing_util['abort'] = 1
            print(f'  time limit exceeded! {curr_time - self.timing_util["starttime"]} ms')

    def _score(self, board:list, move:int) -> int:
        if self.pv_table[0][self.ply] == move: return 20000
        score:int = mvv_lva[board[get_move_source(move)]][board[get_move_target(move)]]
        if get_move_capture(move): score += 10000
        else:
            if self.killer_moves[0][self.ply] == move: score = 9000
            elif self.killer_moves[1][self.ply] == move: score = 8000
            else: score = self.history_moves[board[get_move_source(move)]][get_move_target(move)] + 7000
        return score

    def _sort(self, board:list, move_list:MovesStruct) -> None:
        for c in range(move_list.count):
            if move_list.moves[c].move == self.pv_table[0][0] and move_list.moves[c].move: move_list.moves[c].score = 300000
            else: move_list.moves[c].score = self._score(board, move_list.moves[c].move)
        move_list.moves.sort(reverse=True, key=lambda x:x.score)

    def _root(self, pos, depth:int = OPTIMAL_DEPTH, _timeAllocated:int = TIME_LIMIT_FOR_SEARCH) -> int:
        self._clear()

        score:int = 0
        self.nodes:int = 0
        self._search_depth_from_input:int = depth
        self._search_time_allocation_from_input:int = _timeAllocated
        self._determine_search_limitations()
        self._start_timecontrol()

        if not self.enabled: return 0

        alpha:int = NEG_INF
        beta:int = POS_INF
        absolute_draw:int = 1

        print()
        for c_d in range(1, self._search_depth_from_input + 1):
            score:int = self._alphabeta(alpha, beta, c_d, pos)
            elapsed:int = get_ms(perf_counter()) - self.timing_util['starttime']
            if not elapsed: elapsed = 1
            if self.timing_util['abort']: break
            if self.pv_length[0]:
                print(f'  info depth {c_d} nodes {self.nodes} score {score} nps {get_ms(self.nodes)//elapsed} tbhits {self.tb_hits} time {elapsed} pv', end=' ')
                for _m in range(self.pv_length[0]): print_move(self.pv_table[0][_m])
                if score == -MATE_VAL: self.enabled = 0; print('     IS MATED! | GAMEOVER!\n', end=''); break
                elif score <= -MATE_VAL + MAX_PLY: print('     GETTING MATED!\n', end=''); break
                elif score >= MATE_VAL - MAX_PLY: print('     MATE FOUND!\n', end=''); break
                else: print()
                for _v in range(len(pos.pce_count)):
                    if not _v or _v == 6 or _v == 12: continue
                    if pos.pce_count[_v]: absolute_draw = 0
                if absolute_draw: self.enabled = 0; print('\n  GAME DRAWN!'); break
            else:
                print(f'  info depth {c_d} nodes {self.nodes} score {score} nps {get_ms(self.nodes)//elapsed} time {elapsed}     IS MATED! | GAMEOVER!', end=' ')
                self.enabled = 0; break
        print('\n', end='  ')
        if self.pv_table[0][0]:
            print('bestmove', end=' ')
            print_move(self.pv_table[0][0], '\n')
            pos.make_move(self.pv_table[0][0], ALL_MOVES)
            pos.print_board()
        else: print('\n  bestmove n/a')
        return 1

    def _quiesce(self, alpha:int, beta:int, pos) -> int:
        assert beta > alpha
        self.nodes += 1

        if not (self.nodes & 1023):
            self._checkup()
            if self.timing_util['abort']: return 0

        self.pv_length[self.ply] = self.ply

        if self.ply > MAX_PLY - 1: return beta

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
                self.pv_table[self.ply][self.ply] = move_list.moves[c].move
                for _i in range(self.ply+1, self.pv_length[self.ply+1]): self.pv_table[self.ply][_i] = self.pv_table[self.ply+1][_i]
                self.pv_length[self.ply] = self.pv_length[self.ply+1]
        return alpha

    def _alphabeta(self, alpha:int, beta:int, depth:int, pos) -> int:

        assert depth >= 0
        assert beta > alpha

        self.nodes += 1

        legal_:int = 0
        pv_node:int = beta - alpha > 1
        hash_flag:int = HASH_ALPHA
        b_search_pv:int = 1
        if self.ply and pos.fifty >= 100: return 0
        if depth <= 0: return self._quiesce(alpha, beta, pos)

        if not (self.nodes & 1023):
            self._checkup()
            if self.timing_util['abort']: return 0

        if self.ply > MAX_PLY - 1: return beta

        alpha = max(alpha, -MATE_VAL + self.ply - 1)
        beta = min(beta, MATE_VAL - self.ply)
        if alpha >= beta: return alpha

        score:int = tt.tt_probe(depth, alpha, beta, pos.hash_key)
        if self.ply and score != NO_HASH_ENTRY and not pv_node:
            self.tb_hits += 1
            return score

        self.pv_length[self.ply] = self.ply
        in_check:int = pos.in_check(pos.side)
        if in_check: depth += 1

        if depth >= 3 and (not in_check) and self.ply:
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

            if pos.enpassant != squares['OFFBOARD']: pos.hash_key ^= pos.zobrist.ep[pos.enpassant]
            pos.enpassant = squares['OFFBOARD']

            pos.side ^= 1
            pos.xside ^= 1
            pos.hash_key ^= pos.zobrist.side

            score:int = -self._alphabeta(-beta, -beta + 1, depth - 3, pos)

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

            if self.timing_util['abort']: return 0
            if score >= beta and abs(score) < MATE_VAL: return beta

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

            legal_ = 1

            if b_search_pv:
                score = -self._alphabeta(-beta, -alpha, depth - 1, pos)
            else:
                score = -self._alphabeta(-alpha-1, -alpha, depth - 1, pos)
                if alpha < score < beta: score = -self._alphabeta(-beta, -alpha, depth - 1, pos)

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
