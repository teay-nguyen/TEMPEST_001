from random import choice
from time import time
from evaluation import Evaluate
import time
from MoveOrdering import MoveOrdering
from Transpositions import TranspositionTable
import sys

class DepthLite1():

    def __init__(self):
        self.count = 0
        self.bestMoveInIteration = None
        self.bestEvalInIteration = 0
        self.bestMoveFound = None
        self.bestEvalFound = 0
        self.useIterativeDeepening = True
        self.transpositionTableSize = 6400
        self.POSITIVE_INF = sys.maxsize
        self.NEGATIVE_INF = -sys.maxsize
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

    def Timeout(self, startTime, deadline):
        return (time.time() - startTime) > deadline

    def random_move(self, state):
        moves = state.FilterValidMoves()

        if len(moves) == 0:
            quit()
        else:
            return choice(moves)

    def startSearch(self, state):
        self.bestMoveFound = self.bestMoveInIteration = self.invalidMove
        self.bestEvalFound = self.numCutoffs = self.bestEvalInIteration = self.currentIterativeSearchDepth =  0
        self.abortSearch = False
        self.searchDebugInfo = SearchDebugInfo()

        start = time.time()
        highPerformantDepth = 4
        lowPerformantDepth = 2

        if self.clearTTEachMove:
            self.tt.ClearEntries(self.entries)

        if self.useIterativeDeepening:
            targetDepth = lowPerformantDepth if self.LowPerformanceMode else highPerformantDepth

            for depth in range(1, targetDepth + 1):
                print('Searching Depth:', depth)
                self.Search(state, depth, self.NEGATIVE_INF, self.POSITIVE_INF, 0)

                searchTime = time.time()
                if self.Timeout(start, 5) or self.abortSearch:
                    self.bestMoveFound = self.bestMoveInIteration
                    self.bestEvalFound = self.bestEvalInIteration
                    print('TIME LIMIT EXCEEDED OR ABORT SEARCH ACTIVATED! EXITING SEARCH:', (searchTime - start))
                    break
                else:
                    self.currentIterativeSearchDepth = depth
                    self.bestMoveFound = self.bestMoveInIteration
                    self.bestEvalFound = self.bestEvalInIteration

                    self.searchDebugInfo.lastCompletedDepth = depth
                    self.searchDebugInfo.eval = self.bestEvalFound
                    self.searchDebugInfo.moveVal = 0
                    if (self.bestMoveFound is not None):
                        self.searchDebugInfo.move = self.bestMoveFound.getChessNotation(True)

                    if self.isMateScore(self.bestEvalFound):
                        print('-------------------- FOUND MATE, EXITING SEARCH -------------------')
                        break
        else:
            targetDepth = lowPerformantDepth if self.LowPerformanceMode else highPerformantDepth
            print('Searching Depth:', targetDepth)
            self.Search(state, targetDepth, self.NEGATIVE_INF, self.POSITIVE_INF, 0)
            self.bestMoveFound = self.bestMoveInIteration
            self.bestEvalFound = self.bestEvalInIteration

        print('\n---------------------------------------')
        print('NEXT MOVE:', self.bestMoveFound, self.count, self.bestEvalFound)
        print('---------------------------------------\n')

        end = time.time()
        print(f'TIME TOOK TO GENERATE NEXT MOVE: {end - start}')

        return self.bestMoveFound

    def GetSearchResult(self):
        return (self.bestMoveFound, self.bestEvalFound)

    def EndSearch(self):
        self.abortSearch = True

    def Search(self, state, depth, alpha, beta, plyFromRoot):
        if (self.abortSearch):
            return 0

        if (plyFromRoot > 0):
            if state.ZobristKey in state.RepetitionPositionHistory:
                return 0

            alpha = max(alpha, -self.immediateMateScore + plyFromRoot - 1)
            beta = min(beta, self.immediateMateScore - plyFromRoot)
            if (alpha >= beta):
                return alpha

        ttVal = self.tt.attemptLookup(state, self.entries, depth, plyFromRoot, alpha, beta)
        if (ttVal != self.tt.lookupFailed):
            if (plyFromRoot == 0):
                print('------------------------- TRANSPOSITION FOUND -----------------------------')
                self.bestMoveInIteration = self.tt.getStoredMove(state, self.entries)
                self.bestEvalInIteration = self.entries[self.tt.Index(state)].value

            return ttVal

        if depth == 0:
            eval = self.QuiescenceSearch(state, alpha, beta)
            return eval

        
        self.count += 1
        MoveOrder = MoveOrdering()
        moves = state.FilterValidMoves()
        ordered_moves = MoveOrder.OrderMoves(state, moves)
        FoundPV = False

        if len(moves) == 0:
            if state.inCheck():
                mateScore = self.immediateMateScore - plyFromRoot
                return -mateScore
            else:
                return 0

        bestMoveInPosition = self.invalidMove
        evalType = self.tt.UpperBound

        for move in ordered_moves:
            state.make_move(move, inSearch = True)
            
            if (FoundPV):
                eval = -self.Search(state, depth - 1, -alpha - 1, -alpha, plyFromRoot + 1)
                if eval > alpha and eval < beta:
                    eval = -self.Search(state, depth - 1, -beta, -alpha, plyFromRoot + 1)
            else:
                eval = -self.Search(state, depth - 1, -beta, -alpha, plyFromRoot + 1)
            
            state.undo_move(inSearch = True)
            self.numNodes += 1

            if (eval >= beta):
                self.tt.storeEval(state, self.entries, depth, plyFromRoot, beta, self.tt.LowerBound, move)
                self.numCutoffs += 1
                return beta

            if (eval > alpha):
                evalType = self.tt.Exact
                bestMoveInPosition = move
                alpha = eval
                FoundPV = True

                if plyFromRoot == 0:
                    print('New Best Move Found:', move, eval)
                    self.bestEvalInIteration = eval
                    self.bestMoveInIteration = move

        self.tt.storeEval(state, self.entries, depth, plyFromRoot, alpha, evalType, bestMoveInPosition)
        return alpha

    def QuiescenceSearch(self, state, alpha, beta):
        EvalClass = Evaluate()
        OrderClass = MoveOrdering()
        eval = EvalClass.evaluate(state)

        if (eval >= beta):
            return beta
        if (eval > alpha):
            alpha = eval

        moves = state.FilterValidMoves(onlyCaptures=True)
        ordered_moves = OrderClass.OrderMoves(state, moves)

        for move in ordered_moves:
            state.make_move(move, inSearch = True)
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
        return abs(score) > (self.immediateMateScore - maxMateDepth)

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


class SearchDebugInfo:
    def __init__(self):
        self.lastCompletedDepth = 0
        self.moveVal = 0
        self.move = None
        self.eval = 0
        self.isBook = False
        self.numPositionsEvaluated = 0
