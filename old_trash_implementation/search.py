

'''

    Cleaner implementation of what I had before today
    AlphaBeta + MinMax + other search extensions
    Search diagnostics to track time and nodes
    Although it is kinda weaker though

'''

from __future__ import print_function
from random import choice
import time
from evaluation import Evaluate
from order import MoveOrdering
from tt_util import TranspositionTable
from defs import * #readability
import sys

WINDOW:int = 50
DRAW_OPENING:int = -10
DRAW_ENDGAME:int = 0
MAX_DEPTH:int = 50
MATE_SCORE:int = 100000
POSITIVE_INF:int = sys.maxsize
NEGATIVE_INF:int = -sys.maxsize
DEFAULT_SEARCHDEPTH:int = 3
MAX_PLY = 10
MAX_TIMEALLOC:int = 10 # seconds format
MAX_DEPTH = 50 # the most a serial absearch can handle for me
MAX_DEPTH_THREAD = 100 # this is for when parallel search is performed

MATE_BOUND = (MATE_SCORE - MAX_PLY)
DELTA_CUTOFF = 50

DO_NULL = 1
NO_NULL = 0
IS_PV = 1
NO_PV = 0

class search_limits:
    def __init__(self):
        self._infinite = FALSE
        self._limitedsearch = FALSE
        self._depthsearch = FALSE
        self._fulllimited = TRUE
        self.max_nodes = 200

class search_driver:
    def __init__(self):
        self.move_time = 0
        self.depth = 0
        self.nodes = 0
        self.cutoffs = 0
        self.q_nodes = 0
        self.tt_hit = 0
        self.ply = 0

    def clean_driver(self):
        self.move_time = 0
        self.depth = 0
        self.nodes = 0
        self.cutoffs = 0
        self.q_nodes = 0
        self.tt_hit = 0
        self.ply = 0

class searcher:
    def __init__(self) -> None:
        self.mv_to_play = None
        self.ev_to_play = 0
        self.mv_iter = None
        self.ev_iter = 0
        self._limits = search_limits()
        self._timeAllocated = 0
        self._searchDepth = 0
        self._start = 0
        self.abort:int = FALSE
        self.finished = FALSE
        self.tt = TranspositionTable()
        self.mvor = MoveOrdering()
        self.eval = Evaluate()
        self.tt_entries = self.tt.init_entries()

        self.sd = search_driver()
        self.adjust_searchsettings(self._limits)

    def clean(self) -> None:
        self.mv_to_play = None
        self.ev_to_play = 0
        self.mv_iter = None
        self.ev_iter = 0
        self._limits = search_limits()
        self._timeAllocated = 0
        self._searchDepth = 0
        self._start = 0
        self.abort:int = FALSE
        self.finished = FALSE

        self.sd.clean_driver()
        self.adjust_searchsettings(self._limits)

    def adjust_searchsettings(self, _limits):
        if (_limits._infinite):
            self._timeAllocated = POSITIVE_INF
            self._searchDepth = POSITIVE_INF
        if (_limits._depthsearch):
            self._searchDepth = DEFAULT_SEARCHDEPTH
            self._timeAllocated = POSITIVE_INF
        if (_limits._limitedsearch):
            self._searchDepth = POSITIVE_INF
            self._timeAllocated = MAX_TIMEALLOC
        if (_limits._fulllimited):
            self._searchDepth = DEFAULT_SEARCHDEPTH
            self._timeAllocated = MAX_TIMEALLOC

    def passed_limits(self, elapsed):
        if self.time_check_up(elapsed): return 1
        if (self.sd.nodes >= self._limits.max_nodes): return 1
        return 0

    def search(self, state):
        self.clean()
        self.mv_iter = self.mv_to_play = None
        self.ev_iter = self.ev_to_play = 0
        self.abort = FALSE

    def _nega(self, state, ply, depth, alpha, beta):
        is_pv = beta - alpha != 1
        is_root = ply == 0
        score = -MATE_SCORE
        best_move = None
        pv_found = FALSE

        if (depth <= 0):
            if (state.inCheck()):
                depth = 1
            else:
                return self.quiesce(state, ply + 1, alpha, beta)

        if (self.sd.nodes % 50 == 0):
            if (self.passed_limits(self._start)):
                self.abort = TRUE
                return 0

        if (not is_root):
            if self.is_repetition(state): return 2 - (self.sd.nodes & 0x3)
            if self.sd.nodes >= (MAX_PLY - 1): return 0 if state.inCheck() else self.eval.evaluate(state)

            alpha = max(alpha, -MATE_SCORE + ply)
            beta = min(beta, MATE_SCORE - ply - 1)
            if (alpha >= beta): return alpha

        if (self.tt.getStoredEval(state, self.tt_entries, depth, alpha, beta)) and (not is_pv):
            self.sd.tt_hit = 1
            if (is_root):
                self.ev_iter = self.tt.value
                self.mv_iter = self.tt.getStoredMove(state, self.tt_entries, state.ZobristKey)
            return self.tt.value

        eval_type = self.tt.AlphaBound
        moves = state.FilterValidMoves()
        moves = self.mvor.OrderMoves(state, moves, self.tt_entries)

        for i in range(len(moves)):
            state.make_move(moves[i], inSearch = TRUE)
            if (pv_found):
                score = -self._nega(state, ply + 1, depth - 1, -alpha - 1, -alpha)
                if (score > alpha) and (score < beta):
                    score = -self._nega(state, ply + 1, depth - 1, -beta, -alpha)
            else:
                score = -self._nega(state, ply + 1, depth - 1, -beta, -alpha)
            state.undo_move(inSearch = TRUE)

            self.sd.nodes += 1
            if (self.sd.nodes % 50 == 0):
                if (self.passed_limits(self._start)):
                    self.abort = TRUE
                    break

            if (score >= beta):
                self.tt.storeEval(state, self.tt_entries, depth, beta, self.tt.BetaBound)
                self.tt.storeMove(state, self.tt_entries, depth, moves[i])
                self.sd.cutoffs += 1
                return beta
            if (score > alpha):
                eval_type = self.tt.Exact
                best_move = moves[i]
                alpha = score
                if (is_root):
                    self.mv_iter = moves[i]
                    self.ev_iter = score

        self.tt.storeEval(state, self.tt_entries, depth, alpha, eval_type)
        self.tt.storeMove(state, self.tt_entries, depth, best_move)
        return alpha

    def quiesce(self, state, ply, alpha, beta):
        if self.sd.nodes % 50 == 0:
            if self.passed_limits(self._start):
                self.abort = TRUE
                return 0

        if self.is_repetition(state): return 0
        if ply >= MAX_PLY - 1: return 0 if state.inCheck() else self.eval.evaluate(state)

        score = self.eval.evaluate(state)
        if (score >= beta):
            return beta
        if (score > alpha):
            alpha = score

        moves = state.FilterValidMoves()
        moves = self.mvor.OrderMoves(state, moves, self.tt_entries)
        for i in range(len(moves)):
            if moves[i].pieceCaptured != '--':
                state.make_move(moves[i], inSearch = TRUE)
                self.sd.nodes += 1
                score = -self.quiesce(state, ply + 1, -beta, -alpha)
                state.undo_move(inSearch = TRUE)

                if self.sd.nodes % 50 == 0:
                    if self.passed_limits(self._start):
                        self.abort = TRUE
                        return 0

                if (score >= beta):
                    self.sd.cutoffs += 1
                    return beta
                if (score > alpha):
                    alpha = score
        return alpha

    def time_check_up(self, elapsed):
        if (time.perf_counter() - elapsed) >= (self._timeAllocated): return 1
        return 0

    def random_move(self, state):
        moves = state.FilterValidMoves()
        if len(moves) <= 0: quit()
        else: return choice(moves)

    def is_repetition(self, state) -> int:
        if state.ZobristKey in state.RepetitionPositionHistory: return TRUE
        return FALSE

    def is_mate(self, score:int) -> bool:
        max_depth:int = 1000
        return abs(score) > MATE_SCORE - max_depth

    def ply_to_mate(self, score:int) -> int:
        return MATE_SCORE - score

    def contempt(self, state) -> int:
        val, side = DRAW_OPENING, 'w' if state.whitesturn else 'b'
        if self.eval.materialNoPawns(state, side) < 1300: val = DRAW_ENDGAME
        return val
