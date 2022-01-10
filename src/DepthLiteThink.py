from random import choice
from time import time
from evaluation import Evaluate
import time
from MoveOrdering import MoveOrdering
from Transpositions import TranspositionTable
from Debugging import Debug
import numpy as np

ASPIRATION = 50

class DepthLite1():

    def __init__(self):
        self.count = 0
        self.tt = TranspositionTable()
        self.bestMoveInIteration = None
        self.bestEvalInIteration = 0
        self.bestMoveFound = None
        self.bestEvalFound = 0
        self.useIterativeDeepening = 1
        self.transpositionTableSize = 6400
        self.POSITIVE_INF = np.inf
        self.NEGATIVE_INF = -np.inf
        self.mateScoreInPly = 100000
        self.numNodes = 0
        self.numCutoffs = 0
        self.abortSearch = 0
        self.LowPerformanceMode = 1
        self.searchDebugInfo = None
        self.currentIterativeSearchDepth = 0
        self.tt_entries = self.tt.init_entries()
        self.invalidMove = None
        self.clearTTEachMove = 0
        self.SearchDebug = Debug()
        self.bestMoveInPosition = self.invalidMove
        self.raise_alpha = 0
        self.tagPVLINE = tagPVLINE()
        self.usePrincipalVariation = True
        self.maxDuration = 15 # seconds format
        self.maxDepth = 50

        self.useOpeningBook = 0
        self.maxBookMoves = 40
        self.highPerformantDepth = 10
        self.lowPerformantDepth = 2
        self.MoveOrdering = MoveOrdering()
        self.rootDepth = 1

        self.R = 2

    def countNPS(self, nodes, time): #prototype
        if time == 0: return 0
        pass

    def Timeout(self, startTime, deadline):
        return (time.time() - startTime) >= deadline

    def random_move(self, state):
        moves = state.FilterValidMoves()

        if len(moves) == 0:
            quit()
        return choice(moves)

    def isRepetition(self, state, hashKey):
        for key in range(len(state.RepetitionPositionHistory)):
            table_key = state.RepetitionPositionHistory[key]
            if hashKey == table_key: return 1
        return 0

    def startSearch(self, state):
        self.bestMoveFound = self.bestMoveInIteration = self.invalidMove
        self.bestEvalFound = self.numCutoffs = self.bestEvalInIteration = self.currentIterativeSearchDepth =  0
        self.abortSearch = 0
        self.searchDebugInfo = SearchDebugInfo()
        self.count = eval = 0

        start = time.time()
        move_count = state.FilterValidMoves()
        targetDepth = (self.lowPerformantDepth + 1) if self.LowPerformanceMode else (self.highPerformantDepth + 1)

        eval = self.root_search(state, self.rootDepth, self.NEGATIVE_INF, self.POSITIVE_INF, 0, start)

        if self.useIterativeDeepening:
            for depth in range(2, targetDepth):
                if len(move_count) == 1 & depth == 4: break
                print('[Searching Depth]:', depth)

                eval = self.search_widen(state, depth, eval, start)

                searchTime = time.time()
                if self.Timeout(start, self.maxDuration):
                    self.EndSearch()
                    self.bestMoveFound = self.bestMoveInIteration
                    self.bestEvalFound = self.bestEvalInIteration
                    print('[TIME LIMIT EXCEEDED OR ABORT SEARCH ACTIVATED! EXITING SEARCH]:', (searchTime - start))
                    break
                else:
                    self.currentIterativeSearchDepth = depth
                    self.bestMoveFound = self.bestMoveInIteration
                    self.bestEvalFound = self.bestEvalInIteration

                    self.searchDebugInfo.lastCompletedDepth = depth
                    self.searchDebugInfo.eval = self.bestEvalFound
                    self.searchDebugInfo.moveVal = 0

                    if (self.bestMoveFound != None):
                        self.searchDebugInfo.move = self.bestMoveFound.getChessNotation(True)

                    if self.isMateScore(self.bestEvalFound) or self.gettingMatedScore(self.bestEvalFound):
                        print('-------------------- [FOUND MATE OR IS GETTING MATED, EXITING SEARCH] -------------------')
                        break
        else: 
            print('Searching Depth:', targetDepth)
            self.root_search(state, targetDepth, self.NEGATIVE_INF, self.POSITIVE_INF, 0, start)
            self.bestMoveFound = self.bestMoveInIteration
            self.bestEvalFound = self.bestEvalInIteration
        if self.clearTTEachMove: self.tt.ClearEntries(self.tt_entries)
        if (time.time() - start < 1): time.sleep(1)
        print('\n-------------------------------------------------')
        print('[[NEXT MOVE]:', self.bestMoveFound, ' [Total Nodes Searched]:', self.numNodes, ' [Move Evaluation]:', self.bestEvalFound, '\n   [State ZobristKey]:', state.ZobristKey, '[Num Recursions]:', self.count, \
                '[Total Cutoffs]:', self.numCutoffs, '\n    [Returned Evaluation]:', eval, ']')
        print('-------------------------------------------------\n')
        self.SearchDebug.AppendLog(self.searchDebugInfo) 
        end = time.time()
        print(f'[TIME TOOK TO GENERATE NEXT MOVE: {end - start}]')
        return self.bestMoveFound

    def GetSearchResult(self):
        return (self.bestMoveFound, self.bestEvalFound)

    def EndSearch(self):
        self.abortSearch = 1

    def search_widen(self, state, depth, eval, elapsed):
        temp = eval
        alpha = eval - ASPIRATION
        beta = eval + ASPIRATION

        temp = self.root_search(state, depth, alpha, beta, 0, elapsed)
        if (temp <= alpha or temp >= beta):
            temp = self.root_search(state, depth, self.NEGATIVE_INF, self.POSITIVE_INF, 0, elapsed)
        return temp

    def root_search(self, state, depth, alpha, beta, plyFromRoot, elapsed):
        moves = state.FilterValidMoves()
        ordered_moves = self.MoveOrdering.OrderMoves(state, moves, self.tt_entries)

        self.bestMoveInPosition = self.invalidMove

        for move in ordered_moves:
            self.numNodes += 1
            state.make_move(move, inSearch = True)
            score = -self.ABSearch(state, depth - 1, -beta, -alpha, plyFromRoot + 1, elapsed)
            state.undo_move(inSearch = True)

            if (self.Timeout(elapsed, self.maxDuration)):
                self.EndSearch()
                return 0

            if (score > alpha):
                self.bestMoveInPosition = move

                if (score >= beta):
                    self.tt.storeEval(state, self.tt_entries, depth, score, self.tt.BetaBound)
                    self.tt.storeMove(state, self.tt_entries, depth, move)
                    return beta

                alpha = score
                self.tt.storeEval(state, self.tt_entries, depth, alpha, self.tt.AlphaBound)
                self.tt.storeMove(state, self.tt_entries, depth, self.bestMoveInPosition)
                if (plyFromRoot == 0):
                    print('[New Best Move Found]:', move, ' [Move Evaluation]', score, ' [Nodes Searched]', self.count)
                    self.bestMoveInIteration = move
                    self.bestEvalInIteration = score
                    self.bestMoveFound = self.bestMoveInIteration
                    self.bestEvalFound = self.bestEvalInIteration

        self.tt.storeEval(state, self.tt_entries, depth, alpha, self.tt.Exact)
        if self.bestMoveInPosition != None:
            self.tt.storeMove(state, self.tt_entries, depth, self.bestMoveInPosition)

        return alpha

    def ABSearch(self, state, depth, alpha, beta, plyFromRoot, elapsed):
        if (self.abortSearch):
            self.bestMoveFound = self.bestMoveInIteration
            self.bestEvalFound = self.bestEvalInIteration
            return 0

        if (self.tt.getStoredEval(state, self.tt_entries, depth, alpha, beta)):
            if (self.tt.value > alpha) & (self.tt.value < beta):
                if (plyFromRoot == 0):
                    self.bestMoveFound = self.tt.getStoredMove(state, self.tt_entries, state.ZobristKey)
                    self.bestEvalFound = self.tt.value
                return self.tt.value

        if (state.inCheck()):
            depth += 1

        if (depth <= 0):
            eval = self.QuiescenceSearch(state, alpha, beta, plyFromRoot + 1)
            self.tt.storeEval(state, self.tt_entries, depth, eval, self.tt.Exact)
            return eval

        if (plyFromRoot > 0):
            if self.bestEvalInIteration >= -500:
                if self.isRepetition(state, state.ZobristKey):
                    self.bestMoveFound = self.bestMoveInIteration
                    self.bestEvalFound = self.bestEvalInIteration
                    print('--------------------------------- [REPETITION DETECTED] ---------------------------------')
                    return 0

            if (alpha < -self.mateScoreInPly): alpha = -self.mateScoreInPly
            if (beta > self.mateScoreInPly - 1): beta = self.mateScoreInPly - 1
            if (alpha >= beta):
                return alpha

        self.count += 1
        moves = state.FilterValidMoves()
        ordered_moves = self.MoveOrdering.OrderMoves(state, moves, self.tt_entries)
        self.raise_alpha = 0

        if len(moves) == 0:
            if state.inCheck():
                mateScore = -self.mateScoreInPly + plyFromRoot
                return mateScore
            return 0

        self.bestMoveInPosition = self.invalidMove
        evalType = self.tt.AlphaBound
        
        for move in ordered_moves:
            state.make_move(move, inSearch = True)
            if (self.usePrincipalVariation):
                if not self.raise_alpha:
                    eval = -self.ABSearch(state, depth - 1, -beta, -alpha, plyFromRoot + 1, elapsed)
                else:
                    eval = -self.zwSearch(state, -alpha, depth - 1, plyFromRoot + 1)
                    if (eval > alpha) and (eval < beta):
                        eval = -self.ABSearch(state, depth - 1, -beta, -alpha, plyFromRoot + 1, elapsed)
            else:
                eval = -self.ABSearch(state, depth - 1, -beta, -alpha, plyFromRoot + 1, elapsed)
            state.undo_move(inSearch = True)
            self.numNodes += 1

            if (self.abortSearch) or (self.Timeout(elapsed, self.maxDuration)):
                self.EndSearch()
                self.bestMoveFound = self.bestMoveInIteration
                self.bestEvalFound = self.bestEvalInIteration
                return 0

            if (eval > alpha):
                self.bestMoveInPosition = move
                if (eval >= beta):
                    self.tt.storeEval(state, self.tt_entries, depth, beta, self.tt.BetaBound)
                    self.tt.storeMove(state, self.tt_entries, depth, move)
                    evalType = self.tt.BetaBound
                    alpha = beta
                    break

                evalType = self.tt.Exact
                self.raise_alpha = 1
                alpha = eval
                if plyFromRoot <= 0:
                    print('[New Best Move Found]:', move, ' [Move Evaluation]:', eval, ' [Num Nodes Searched]:', self.numNodes)
                    self.bestEvalInIteration = eval
                    self.bestMoveInIteration = move
                    self.bestMoveFound = self.bestMoveInIteration
                    self.bestEvalFound = self.bestEvalInIteration

        self.tt.storeEval(state, self.tt_entries, depth, alpha, evalType)
        if self.bestMoveInPosition != None:
            self.tt.storeMove(state, self.tt_entries, depth, self.bestMoveInPosition)
        return alpha

    def zwSearch(self, state, beta, depth, plyFromRoot):
        if depth == 0: return self.QuiescenceSearch(state, beta - 1, beta, plyFromRoot + 1)

        moves = state.FilterValidMoves()
        ordered_moves = self.MoveOrdering.OrderMoves(state, moves, self.tt_entries)

        for move in ordered_moves:
            state.make_move(move, inSearch = True)
            score = -self.zwSearch(state, 1 - beta, depth - 1, plyFromRoot + 1)
            state.undo_move()
            if (score >= beta):
                return beta

        return beta - 1

    def QuiescenceSearch(self, state, alpha, beta, ply):
        EvalClass = Evaluate()
        eval = EvalClass.evaluate(state)

        if (eval > alpha):
            if (eval >= beta):
                return eval
            alpha = eval

        if (eval >= beta):
            return beta
        if (eval > alpha):
            alpha = eval

        if (ply > 0):
            if self.bestEvalInIteration >= -500:
                if self.isRepetition(state, state.ZobristKey):
                    self.bestMoveFound = self.bestMoveInIteration
                    self.bestEvalFound = self.bestEvalInIteration
                    print('--------------------------------- [REPETITION DETECTED] ---------------------------------')
                    return 0

        moves = state.FilterValidMoves(onlyCaptures = True)
        ordered_moves = self.MoveOrdering.OrderMoves(state, moves, self.tt_entries)

        for move in ordered_moves:
            state.make_move(move, inSearch = True)
            eval = -self.QuiescenceSearch(state, -beta, -alpha, ply + 1)
            state.undo_move(inSearch = True)

            if (eval > alpha):
                if (eval >= beta):
                    return eval
                alpha = eval

        return alpha

    def isMateScore(self, score):
        maxMateDepth = 1000
        return abs(score) >= (self.mateScoreInPly - maxMateDepth)

    def gettingMatedScore(self, score):
        maxMateDepth = 1000
        return abs(score) <= (-self.mateScoreInPly + maxMateDepth)

    def ResetDebugInfo(self):
        if self.searchDebugInfo is not None:
            self.searchDebugInfo.lastCompletedDepth = 0
            self.searchDebugInfo.moveVal = 0
            self.searchDebugInfo.move = None
            self.searchDebugInfo.eval = 0
            self.searchDebugInfo.isBook = False
            self.searchDebugInfo.numPositionsEvaluated = 0
        else:
            self.searchDebugInfo = SearchDebugInfo()

class tagPVLINE:
    def __init__(self) -> None:
        self.PVLINE = []
        self.PVLength = 9

class SearchDebugInfo:
    def __init__(self):
        self.lastCompletedDepth = 0
        self.moveVal = 0
        self.move = None
        self.eval = 0
        self.isBook = False
        self.numPositionsEvaluated = 0
