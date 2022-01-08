from random import choice
from time import time
from evaluation import Evaluate
import time
from MoveOrdering import MoveOrdering
from Transpositions import TranspositionTable
from Debugging import Debug
import numpy as np

class DepthLite1():

    def __init__(self):
        self.count = 0
        self.bestMoveInIteration = None
        self.bestEvalInIteration = 0
        self.bestMoveFound = None
        self.bestEvalFound = 0
        self.useIterativeDeepening = True
        self.transpositionTableSize = 6400
        self.POSITIVE_INF = np.inf
        self.NEGATIVE_INF = -np.inf
        self.immediateMateScore = 100000
        self.numNodes = 0
        self.numCutoffs = 0
        self.abortSearch = False
        self.LowPerformanceMode = True
        self.searchDebugInfo = None
        self.currentIterativeSearchDepth = 0
        self.entries = {}
        self.invalidMove = None
        self.clearTTEachMove = False
        self.tt = TranspositionTable()
        self.SearchDebug = Debug()
        self.currentTrackedMove = self.invalidMove
        self.bestMoveInPosition = self.invalidMove
        self.PVFound = False
        self.tagPVLINE = tagPVLINE()
        self.usePrincipalVariation = False
        self.maxDuration = 10 # seconds format

        self.useOpeningBook = False
        self.maxBookMoves = 40
        self.highPerformantDepth = 10
        self.lowPerformantDepth = 2
        self.MoveOrdering = MoveOrdering()

    def Timeout(self, startTime, deadline):
        return (time.time() - startTime) > deadline

    def random_move(self, state):
        moves = state.FilterValidMoves()

        if len(moves) == 0:
            quit()
        return choice(moves)

    def startSearch(self, state):
        if self.useOpeningBook:
            if len(state.move_log) <= self.maxBookMoves:
                pass

        self.bestMoveFound = self.bestMoveInIteration = self.invalidMove
        self.bestEvalFound = self.numCutoffs = self.bestEvalInIteration = self.currentIterativeSearchDepth =  0
        self.abortSearch = False
        self.searchDebugInfo = SearchDebugInfo()
        self.count = 0

        start = time.time()

        if self.useIterativeDeepening:
            targetDepth = (self.lowPerformantDepth + 1) if self.LowPerformanceMode else (self.highPerformantDepth + 1)

            for depth in range(1, targetDepth):
                print('[Searching Depth]:', depth)

                self.root_search(state, depth, self.NEGATIVE_INF, self.POSITIVE_INF, 0)

                searchTime = time.time()
                if self.Timeout(start, self.maxDuration) or (self.abortSearch):
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

                    if self.isMateScore(self.bestEvalFound) or (abs(self.bestEvalFound) <= (-self.immediateMateScore + 1000)):
                        print('-------------------- [FOUND MATE OR IS GETTING MATED, EXITING SEARCH] -------------------')
                        break
        else:
            targetDepth = self.lowPerformantDepth if self.LowPerformanceMode else self.highPerformantDepth
            
            print('Searching Depth:', targetDepth)

            self.root_search(state, targetDepth, self.NEGATIVE_INF, self.POSITIVE_INF, 0)
            self.bestMoveFound = self.bestMoveInIteration
            self.bestEvalFound = self.bestEvalInIteration

        if self.clearTTEachMove:
            self.tt.ClearEntries(self.entries)

        if (time.time() - start < 1):
            time.sleep(1)

        print('\n-------------------------------------------------')
        print('[[NEXT MOVE]:', self.bestMoveFound, ' [Total Nodes Searched]:', self.numNodes, ' [Move Evaluation]:', self.bestEvalFound, '\n   [State ZobristKey]:', state.ZobristKey, '[Num Recursions]:', self.count, ']')
        print('-------------------------------------------------\n')

        self.SearchDebug.AppendLog(self.searchDebugInfo)
        
        end = time.time()
        print(f'[TIME TOOK TO GENERATE NEXT MOVE: {end - start}]')

        return self.bestMoveFound

    def GetSearchResult(self):
        return (self.bestMoveFound, self.bestEvalFound)

    def EndSearch(self):
        self.abortSearch = True

    def root_search(self, state, depth, alpha, beta, plyFromRoot):
        moves = state.FilterValidMoves()
        ordered_moves = self.MoveOrdering.OrderMoves(state, moves, self.entries)

        self.bestMoveInPosition = self.invalidMove

        for move in ordered_moves:
            self.numNodes += 1
            state.make_move(move, inSearch = True)
            score = -self.ABSearch(state, depth - 1, -beta, -alpha, plyFromRoot + 1)
            state.undo_move(inSearch = True)

            if (self.abortSearch):
                return 0

            if (score > alpha):
                alpha = score
                self.bestMoveInPosition = move

                if (plyFromRoot == 0):
                    print('[New Best Move Found]:', move, ' [Move Evaluation]', score, ' [Nodes Searched]', self.count)
                    self.bestMoveInIteration = move
                    self.bestEvalInIteration = score

        if self.bestMoveInPosition != None:
            self.tt.storeMove(state, self.entries, depth, self.bestMoveInPosition)

        return alpha

    def ABSearch(self, state, depth, alpha, beta, plyFromRoot):
        start = time.time()
        if (self.abortSearch):
            self.bestMoveFound = self.bestMoveInIteration
            self.bestEvalFound = self.bestEvalInIteration
            return 0

        if (self.tt.attemptLookup(state, self.entries, depth, alpha, beta)):
            if (plyFromRoot > 0):
                self.bestMoveInIteration = self.tt.getStoredMove(state, self.entries, state.ZobristKey)
                self.bestEvalInIteration = self.tt.value
            return self.tt.value

        if (depth <= 0):
            eval = self.QuiescenceSearch(state, alpha, beta)
            self.tt.storeEval(state, self.entries, depth, eval, self.tt.Exact)

            return eval

        if (depth >= 3 and not state.inCheck()):
            tempEP = state.epPossible

            state.whitesturn = not state.whitesturn
            state.epPossible = ()
            eval = -self.ABSearch(state, depth - 1 - 2, -beta, -beta + 1, plyFromRoot + 1)
            state.whitesturn = not state.whitesturn

            state.epPossible = tempEP

            if (eval >= beta):
                self.tt.storeEval(state, self.entries, depth, beta, self.tt.BetaBound)
                return beta

        if (plyFromRoot > 0):
            if self.bestEvalInIteration >= -500:
                if state.ZobristKey in state.RepetitionPositionHistory:
                    self.bestMoveFound = self.bestMoveInIteration
                    self.bestEvalFound = self.bestEvalInIteration
                    print('--------------------------------- [REPETITION DETECTED] ---------------------------------')
                    return 0

            alpha = max(alpha, -self.immediateMateScore + plyFromRoot)
            beta = min(beta, self.immediateMateScore - plyFromRoot)
            if (alpha >= beta):
                return alpha

        self.count += 1
        moves = state.FilterValidMoves()
        ordered_moves = self.MoveOrdering.OrderMoves(state, moves, self.entries)
        self.FoundPV = False
        self.tagPVLINE.PVLINE = []
        can_move = 0

        if len(moves) == 0:
            if state.inCheck():
                mateScore = -self.immediateMateScore + plyFromRoot
                return mateScore
            else:
                return 0

        self.bestMoveInPosition = self.invalidMove
        evalType = self.tt.AlphaBound
        
        for move in ordered_moves:
            state.make_move(move, inSearch = True)

            self.currentTrackedMove = move

            if (self.usePrincipalVariation):
                if (self.FoundPV):
                    eval = -self.ABSearch(state, depth - 1, -alpha - 1, -alpha, plyFromRoot + 1)
                    if (eval > alpha) and (eval < beta):
                        eval = -self.ABSearch(state, depth - 1, -beta, -alpha, plyFromRoot + 1)
                else:
                    eval = -self.ABSearch(state, depth - 1, -beta, -alpha, plyFromRoot + 1)
            else:
                eval = -self.ABSearch(state, depth - 1, -beta, -alpha, plyFromRoot + 1)
            
            state.undo_move(inSearch = True)
            self.numNodes += 1

            if (self.abortSearch):
                self.bestMoveFound = self.bestMoveInIteration
                self.bestEvalFound = self.bestEvalInIteration
                return 0

            if (eval > self.NEGATIVE_INF):
                can_move = 1

            if (eval >= beta):
                self.tt.storeEval(state, self.entries, depth, beta, self.tt.BetaBound)
                self.tt.storeMove(state, self.entries, depth, move)
                self.numCutoffs += 1
                return beta

            if (eval > alpha):
                evalType = self.tt.Exact
                self.bestMoveInPosition = move
                self.FoundPV = True
                alpha = eval

                self.tt.storeMove(state, self.entries, depth, move)

                if plyFromRoot == 0:
                    print('[New Best Move Found]:', move, ' [Move Evaluation]:', eval, ' [Nodes Searched]:', self.count)
                    self.bestEvalInIteration = eval
                    self.bestMoveInIteration = move

        if (not can_move):
            if state.inCheck():
                return -self.immediateMateScore + plyFromRoot
            else:
                return 0

        self.tt.storeEval(state, self.entries, depth, alpha, evalType)
        self.tt.storeMove(state, self.entries, depth, self.bestMoveInPosition)
        return alpha

    def QuiescenceSearch(self, state, alpha, beta):
        EvalClass = Evaluate()
        eval = EvalClass.evaluate(state, False)

        if (eval >= beta):
            return beta
        if (eval > alpha):
            alpha = eval

        moves = state.FilterValidMoves(onlyCaptures=True)
        ordered_moves = self.MoveOrdering.OrderMoves(state, moves, self.entries)

        for move in ordered_moves:
            state.make_move(move, inSearch = True)

            self.currentTrackedMove = move
            eval = -self.QuiescenceSearch(state, -beta, -alpha)
            
            state.undo_move(inSearch = True)

            if (eval >= beta):
                self.numCutoffs += 1
                return beta
            if (eval > alpha):
                alpha = eval

        return alpha

    def isMateScore(self, score):
        maxMateDepth = 1000
        return abs(score) >= (self.immediateMateScore - maxMateDepth)

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
