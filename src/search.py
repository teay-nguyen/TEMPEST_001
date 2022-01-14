from __future__ import print_function
from random import choice
from time import time
from evaluation import Evaluate
import time
from order import MoveOrdering
from tt_util import TranspositionTable
from debug import Debug

ASPIRATION:int = 50
DRAW_OPENING:int = -10
DRAW_ENDGAME:int = 0

class searcher:
    def __init__(self):
        self.count: int
        self.tt: TranspositionTable
        self.useIterativeDeepening: int
        self.bestEvalFound: int
        self.POSITIVE_INF: int
        self.NEGATIVE_INF: int
        self.LowPerformanceMode: int
        self.lowPerformantDepth: int
        self.highPerformantDepth: int
        self.max_ply: int
        self.maxBookMoves: int
        self.maxDepth: int
        self.maxDuration: int

        self.count:int = 0
        self.tt:TranspositionTable = TranspositionTable()
        self.bestMoveInIteration = None
        self.bestEvalInIteration:int = 0
        self.bestMoveFound = None
        self.bestEvalFound:int = 0
        self.useIterativeDeepening:int = 1
        self.POSITIVE_INF:int = 99999999999
        self.NEGATIVE_INF:int = -99999999999
        self.mateScoreInPly:int = 100000
        self.numNodes:int = 0
        self.numCutoffs:int = 0
        self.abortSearch:int = 0
        self.LowPerformanceMode:int = 1
        self.searchDebugInfo:SearchDebugInfo = SearchDebugInfo()
        self.currentIterativeSearchDepth:int = 0
        self.tt_entries:list = self.tt.init_entries()
        self.pv_entries:list = self.tt.init_entries()
        self.invalidMove:None = None
        self.clearTTEachMove:int = 0
        self.SearchDebug:Debug = Debug()
        self.bestMoveInPosition = self.invalidMove
        self.raise_alpha:int = 0
        self.tagPVLINE:pv_line = pv_line()
        self.usePrincipalVariation:int = 1
        self.maxDuration:int = 15 # seconds format
        self.maxDepth:int = 50

        self.useOpeningBook:int = 0
        self.maxBookMoves:int = 40
        self.highPerformantDepth:int = self.maxDepth
        self.lowPerformantDepth:int = 2
        self.MoveOrdering:MoveOrdering = MoveOrdering()
        self.rootDepth:int = 1
        self.max_ply:int = 10
        self.evaluate:Evaluate = Evaluate()

        self.R:int = 2

    def random_move(self, state):
        moves: list = state.FilterValidMoves()
        if len(moves) == 0: quit()
        return choice(moves)
    def isRepetition(self, state, hashKey:int) -> int:
        if hashKey in state.RepetitionPositionHistory: return 1
        return 0
    def countNPS(self, nodes, elapsed:float) -> float:
        if (elapsed == 0): return 0
        return nodes // elapsed

    def startSearch(self, state):
        targetDepth: int
        eval: int
        start: float
        self.count: int
        self.abortSearch: int

        self.bestMoveFound = self.bestMoveInIteration = self.invalidMove
        self.bestEvalFound = self.numCutoffs = self.bestEvalInIteration = self.currentIterativeSearchDepth =  0
        self.abortSearch: int = 0
        self.searchDebugInfo: SearchDebugInfo = SearchDebugInfo()
        self.count: int = 0
        start:float = time.time()
        targetDepth:int = ((self.lowPerformantDepth + 1) if self.LowPerformanceMode else (self.highPerformantDepth + 1))\
                            if self.useIterativeDeepening else (self.lowPerformantDepth if self.LowPerformanceMode else self.highPerformantDepth);
        print('[Performing Root Search At Depth 1...]')

        eval = self.root_search(state, self.rootDepth, self.NEGATIVE_INF, self.POSITIVE_INF, 0, start) # rootDepth = 1

        if self.useIterativeDeepening:
            for depth in range(2, targetDepth):
                print('[Searching Depth]:', depth)
                eval = self.search_widen(state, depth, eval, start)
                if self.Timeout(start, self.maxDuration) or self.abortSearch:
                    self.EndSearch()
                    self.bestMoveFound = self.bestMoveInIteration
                    self.bestEvalFound = self.bestEvalInIteration
                    print('[TIME LIMIT EXCEEDED OR ABORT SEARCH ACTIVATED! EXITING SEARCH]:', (time.time() - start))
                    break
                else:
                    self.currentIterativeSearchDepth = depth
                    self.bestMoveFound = self.bestMoveInIteration
                    self.bestEvalFound = self.bestEvalInIteration
                    self.searchDebugInfo.lastCompletedDepth = depth
                    self.searchDebugInfo.eval = self.bestEvalFound
                    self.searchDebugInfo.moveVal = 0
                    if (self.bestMoveFound != None): self.searchDebugInfo.move = self.bestMoveFound.getChessNotation(True)
                    if self.isMateScore(self.bestEvalFound):
                        print('-------------------- [FOUND MATE OR IS GETTING MATED, EXITING SEARCH] -------------------')
                        break
        else: 
            print('Searching Depth:', targetDepth)
            self.root_search(state, targetDepth, self.NEGATIVE_INF, self.POSITIVE_INF, 0, start)
            self.bestMoveFound = self.bestMoveInIteration
            self.bestEvalFound = self.bestEvalInIteration
        if self.clearTTEachMove: self.tt.ClearEntries(self.tt_entries)
        print('\n-------------------------------------------------')
        print('[[NEXT MOVE]:', self.bestMoveFound, ' [Total Nodes Searched]:', self.numNodes, ' [Move Evaluation]:', self.bestEvalFound, '\n   [State ZobristKey]:', state.ZobristKey, '[Num Recursions]:', self.count, \
                '[Total Cutoffs]:', self.numCutoffs, '\n    [Returned Evaluation]:', eval, ']')
        print('-------------------------------------------------')
        self.SearchDebug.AppendLog(self.searchDebugInfo) 
        return self.bestMoveFound

    def GetSearchResult(self)->tuple: return (self.bestMoveFound, self.bestEvalFound)
    def EndSearch(self)->None: self.abortSearch = 1

    def search_widen(self, state, depth:int, eval:int, elapsed:float)->int:
        temp: int
        alpha: int
        beta: int

        temp:int = eval
        alpha:int = eval - ASPIRATION
        beta:int = eval + ASPIRATION

        temp:int = self.root_search(state, depth, alpha, beta, 0, elapsed)
        if (temp <= alpha or temp >= beta): temp = self.root_search(state, depth, self.NEGATIVE_INF, self.POSITIVE_INF, 0, elapsed)
        return temp

    def root_search(self, state, depth:int, alpha:int, beta:int, plyFromRoot:int, elapsed:float)->int:
        ordered_moves: list
        moves: list
        moves: list
        score: int

        moves = state.FilterValidMoves()
        ordered_moves = self.MoveOrdering.OrderMoves(state, moves, self.tt_entries)
        self.count += 1
        self.bestMoveInPosition = self.invalidMove

        if (plyFromRoot >= self.max_ply - 1): return self.evaluate.evaluate(state)
        
        for i in range(len(ordered_moves)):
            self.numNodes += 1
            state.make_move(ordered_moves[i], inSearch = True)
            score = -self.ABSearch(state, depth - 1, -beta, -alpha, plyFromRoot + 1, elapsed, self.mateScoreInPly)
            state.undo_move(inSearch = True)
            if (self.Timeout(elapsed, self.maxDuration) or self.abortSearch):
                self.EndSearch()
                return 0
            if (score > alpha):
                self.bestMoveInPosition = ordered_moves[i]
                if (score >= beta):
                    self.tt.storeEval(state, self.tt_entries, depth, score, self.tt.BetaBound)
                    self.tt.storeMove(state, self.tt_entries, depth, ordered_moves[i])
                    return beta
                alpha = score
                self.tt.storeEval(state, self.tt_entries, depth, alpha, self.tt.AlphaBound)
                self.tt.storeMove(state, self.tt_entries, depth, self.bestMoveInPosition)
                if (plyFromRoot == 0):
                    print('[New Best Move Found]:', ordered_moves[i], ' [Move Evaluation]', score, ' [Nodes Searched]', self.count)
                    self.bestMoveInIteration = ordered_moves[i]
                    self.bestEvalInIteration = score
                    self.bestMoveFound = self.bestMoveInIteration
                    self.bestEvalFound = self.bestEvalInIteration
        if (self.Timeout(elapsed, self.maxDuration)) or self.abortSearch:
            self.EndSearch()
            return 0
        self.tt.storeEval(state, self.tt_entries, depth, alpha, self.tt.Exact)
        self.tt.storeMove(state, self.tt_entries, depth, self.bestMoveInPosition)
        return alpha

    def ABSearch(self, state, depth:int, alpha:int, beta:int, plyFromRoot:int, elapsed:float, mate:int)->int:
        eval: int
        evalType: int
        side_in_check: bool
        ordered_moves: list
        moves: list

        self.count += 1
        moves:list = state.FilterValidMoves()
        ordered_moves:list = self.MoveOrdering.OrderMoves(state, moves, self.tt_entries)
        self.raise_alpha:int = 0
        self.legal:int = 0
        self.bestMoveInPosition = None
        eval:int = self.NEGATIVE_INF
        side_in_check:bool = state.inCheck()
        evalType:int = self.tt.AlphaBound

        if (self.abortSearch) or self.Timeout(elapsed, self.maxDuration): return 0
        if (depth <= 0): return self.QuiescenceSearch(state, alpha, beta, plyFromRoot + 1, elapsed)
        if self.isRepetition(state, state.ZobristKey) and plyFromRoot:
            print('--------------------------------- [REPETITION DETECTED] ---------------------------------')
            return self.contempt(state)
        alpha = max(alpha, -self.mateScoreInPly + plyFromRoot)
        beta = min(beta, self.mateScoreInPly - plyFromRoot)
        if (alpha >= beta): return alpha
        if (self.tt.getStoredEval(state, self.tt_entries, depth, alpha, beta)):
            tt_val = self.tt.value
            if (tt_val > alpha) and (tt_val < beta): return tt_val
        if (plyFromRoot >= self.max_ply - 1): return self.evaluate.evaluate(state)

        for i in range(len(ordered_moves)):
            state.make_move(ordered_moves[i], inSearch = True)
            if (self.usePrincipalVariation):
                if not self.raise_alpha:
                    eval = -self.ABSearch(state, depth - 1, -beta, -alpha, plyFromRoot + 1, elapsed, mate - 1)
                else:
                    eval = -self.zwSearch(state, -alpha, depth - 1, plyFromRoot + 1, elapsed)
                    if (eval > alpha) and (eval < beta): eval = -self.ABSearch(state, depth - 1, -beta, -alpha, plyFromRoot + 1, elapsed, mate - 1)
            else: eval = -self.ABSearch(state, depth - 1, -beta, -alpha, plyFromRoot + 1, elapsed, mate - 1)

            state.undo_move(inSearch = True)
            self.numNodes += 1
            if (self.abortSearch) or (self.Timeout(elapsed, self.maxDuration)):
                self.EndSearch()
                return 0
            if (eval > alpha):
                self.bestMoveInPosition = ordered_moves[i]
                if (eval >= beta):
                    self.tt.storeEval(state, self.tt_entries, depth, beta, self.tt.BetaBound)
                    self.tt.storeMove(state, self.tt_entries, depth, ordered_moves[i])
                    evalType = self.tt.BetaBound
                    alpha = beta
                    break
                evalType = self.tt.Exact
                self.raise_alpha = 1
                alpha = eval
                if plyFromRoot <= 0:
                    print('[New Best Move Found]:', ordered_moves[i], ' [Move Evaluation]:', eval, ' [Num Nodes Searched]:', self.numNodes)
                    self.bestEvalInIteration = eval
                    self.bestMoveInIteration = ordered_moves[i]
                    self.bestMoveFound = self.bestMoveInIteration
                    self.bestEvalFound = self.bestEvalInIteration
            self.legal += 1
        if len(moves) == 0:
            if side_in_check: return -self.mateScoreInPly + plyFromRoot
            return 0
        if self.abortSearch or (self.Timeout(elapsed, self.maxDuration)):
            self.EndSearch()
            return 0
        self.tt.storeEval(state, self.tt_entries, depth, alpha, evalType)
        self.tt.storeMove(state, self.tt_entries, depth, self.bestMoveInPosition)
        return alpha

    def zwSearch(self, state, beta:int, depth:int, plyFromRoot:int, elapsed:float)->int:
        if depth <= 0: return self.QuiescenceSearch(state, beta - 1, beta, plyFromRoot + 1, elapsed)
        if (plyFromRoot >= self.max_ply - 1): return self.evaluate.evaluate(state)
        moves = state.FilterValidMoves()
        ordered_moves = self.MoveOrdering.OrderMoves(state, moves, self.tt_entries)

        for move in ordered_moves:
            state.make_move(move, inSearch = True)
            score = -self.zwSearch(state, 1 - beta, depth - 1, plyFromRoot + 1, elapsed)
            state.undo_move()
            if self.abortSearch or (self.Timeout(elapsed, self.maxDuration)):
                self.EndSearch()
                return 0
            if (score >= beta): return beta
        if self.abortSearch or (self.Timeout(elapsed, self.maxDuration)):
            self.EndSearch()
            return 0
        return beta - 1

    def QuiescenceSearch(self, state, alpha:int, beta:int, ply:int, elapsed:float)->int:
        eval:int = self.evaluate.evaluate(state)

        if (ply >= self.max_ply - 1): return eval
        if (eval > alpha):
            if (eval >= beta): return eval
            alpha = eval

        if self.isRepetition(state, state.ZobristKey) and ply:
            print('--------------------------------- [REPETITION DETECTED] ---------------------------------')
            return self.contempt(state)

        moves = state.GenerateCaptures()
        ordered_moves = self.MoveOrdering.OrderMoves(state, moves, self.tt_entries)

        for move in ordered_moves:
            state.make_move(move, inSearch = True)
            eval = -self.QuiescenceSearch(state, -beta, -alpha, ply + 1, elapsed)
            state.undo_move(inSearch = True)
            if self.abortSearch or (self.Timeout(elapsed, self.maxDuration)):
                self.EndSearch()
                return 0
            if (eval > alpha):
                if (eval >= beta): return eval
                alpha = eval
        return alpha

    def contempt(self, state)->int:
        value = DRAW_OPENING
        side = 'w' if state.whitesturn else 'b'
        if (self.evaluate.materialNoPawns(state, side) < 1300): value = DRAW_ENDGAME
        return (1 * value) if state.whitesturn else (-1 * value)
    def Timeout(self, startTime: float, deadline: int) -> bool: return (time.time() - startTime) >= deadline
    def isMateScore(self, score)->bool:
        maxMateDepth = 1000
        if abs(score) > (self.mateScoreInPly - maxMateDepth): print(f'Mate in {(self.mateScoreInPly - score + 1) // 2}')
        if -abs(score) < (-self.mateScoreInPly + maxMateDepth): print(f'Mated in {(self.mateScoreInPly - score + 1) // 2}')
        return abs(score) > (self.mateScoreInPly - maxMateDepth)

    def ResetDebugInfo(self)->None:
        if self.searchDebugInfo is not None:
            self.searchDebugInfo.lastCompletedDepth = 0
            self.searchDebugInfo.moveVal = 0
            self.searchDebugInfo.move = None
            self.searchDebugInfo.eval = 0
            self.searchDebugInfo.isBook = False
            self.searchDebugInfo.numPositionsEvaluated = 0
        else: self.searchDebugInfo = SearchDebugInfo()

class pv_line:
    def __init__(self) -> None:
        self.PV_LINE = []

class SearchDebugInfo:
    def __init__(self) -> None:
        self.lastCompletedDepth = 0
        self.moveVal = 0
        self.move = None
        self.eval = 0
        self.isBook = False
        self.numPositionsEvaluated = 0
