from random import choice
from time import time
from evaluation import Evaluate
import time
from MoveOrdering import MoveOrdering
from Transpositions import TranspositionTable
from Debugging import Debug

class DepthLite1():

    def __init__(self):
        self.count = 0
        self.bestMoveInIteration = None
        self.bestEvalInIteration = 0
        self.bestMoveFound = None
        self.bestEvalFound = 0
        self.useIterativeDeepening = True
        self.transpositionTableSize = 6400
        self.POSITIVE_INF = 9999999999
        self.NEGATIVE_INF = -9999999999
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
        self.usePrincipalVariation = True

        self.useOpeningBook = False
        self.maxBookMoves = 40
        self.highPerformantDepth = 4
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
            if len(state.move_log):
                pass

        self.bestMoveFound = self.bestMoveInIteration = self.invalidMove
        self.bestEvalFound = self.numCutoffs = self.bestEvalInIteration = self.currentIterativeSearchDepth =  0
        self.abortSearch = False
        self.searchDebugInfo = SearchDebugInfo()
        self.count = 0

        start = time.time()

        if self.clearTTEachMove:
            self.tt.ClearEntries(self.entries)

        if self.useIterativeDeepening:
            targetDepth = (self.lowPerformantDepth + 1) if self.LowPerformanceMode else (self.highPerformantDepth + 1)

            for depth in range(1, targetDepth):
                print('[Searching Depth]:', depth)
                self.Search(state, depth, self.NEGATIVE_INF, self.POSITIVE_INF, 0)

                searchTime = time.time()
                if self.Timeout(start, 10) or self.abortSearch:
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

                    if self.isMateScore(self.bestEvalFound):
                        print('-------------------- [FOUND MATE, EXITING SEARCH] -------------------')
                        break
        else:
            targetDepth = self.lowPerformantDepth if self.LowPerformanceMode else self.highPerformantDepth
            
            print('Searching Depth:', targetDepth)
            self.Search(state, targetDepth, self.NEGATIVE_INF, self.POSITIVE_INF, 0)
            self.bestMoveFound = self.bestMoveInIteration
            self.bestEvalFound = self.bestEvalInIteration

        print('\n-------------------------------------------------')
        print('[[NEXT MOVE]:', self.bestMoveFound, ' [Total Nodes Searched]:', self.numNodes, ' [Move Evaluation]:', self.bestEvalFound, '\n   [State ZobristKey]:', state.ZobristKey, '[Num Recursions]:', self.count, ']')
        print('-------------------------------------------------\n')

        print('\n', state.board ,'\n')

        self.SearchDebug.AppendLog(self.searchDebugInfo)
        
        end = time.time()
        print(f'[TIME TOOK TO GENERATE NEXT MOVE: {end - start}]')

        return self.bestMoveFound

    def GetSearchResult(self):
        return (self.bestMoveFound, self.bestEvalFound)

    def EndSearch(self):
        self.abortSearch = True

    def Search(self, state, depth, alpha, beta, plyFromRoot):
        if (self.abortSearch):
            self.bestMoveFound = self.bestMoveInIteration
            self.bestEvalFound = self.bestEvalInIteration
            return 0

        if (depth >= 3 and not state.inCheck()):
            state.whitesturn = not state.whitesturn
            state.epPossible = ()
            eval = -self.Search(state, depth - 1 - 2, -beta, -beta + 1, plyFromRoot + 1)
            state.whitesturn = not state.whitesturn
            if (eval >= beta):
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

        ttVal = self.tt.attemptLookup(state, self.entries, depth, plyFromRoot, alpha, beta)
        if (ttVal != self.tt.lookupFailed):
            if (plyFromRoot == 0):
                print('-------------------------------------- [TRANSPOSITION FOUND] --------------------------------------')
                self.bestMoveInIteration = self.tt.getStoredMove(state, self.entries)
                self.bestEvalInIteration = self.entries[self.tt.Index(state)].value

            return ttVal

        if depth == 0:
            eval = self.QuiescenceSearch(state, alpha, beta)
            return eval
 
        self.count += 1
        moves = state.FilterValidMoves()
        ordered_moves = self.MoveOrdering.OrderMoves(state, moves)
        self.FoundPV = False
        self.tagPVLINE.PVLINE = []

        if len(moves) == 0:
            if state.inCheck():
                mateScore = self.immediateMateScore - plyFromRoot
                return -mateScore
            else:
                return 0

        self.bestMoveInPosition = self.invalidMove
        evalType = self.tt.UpperBound
        
        for move in ordered_moves:
            state.make_move(move, inSearch = True)

            self.currentTrackedMove = move

            if (self.usePrincipalVariation):
                if (self.FoundPV):
                    eval = -self.Search(state, depth - 1, -alpha - 1, -alpha, plyFromRoot + 1)
                    if (eval > alpha) and (eval < beta):
                        eval = -self.Search(state, depth - 1, -beta, -alpha, plyFromRoot + 1)
                else:
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
                self.bestMoveInPosition = move
                alpha = eval
                self.FoundPV = True

                if plyFromRoot == 0:
                    print('[New Best Move Found]:', move, ' [Move Evaluation]', eval, ' [Nodes Searched]', self.count)
                    self.bestEvalInIteration = eval
                    self.bestMoveInIteration = move

        self.tt.storeEval(state, self.entries, depth, plyFromRoot, alpha, evalType, self.bestMoveInPosition)
        return alpha

    def QuiescenceSearch(self, state, alpha, beta):
        EvalClass = Evaluate()
        eval = EvalClass.evaluate(state, False)

        if (eval >= beta):
            return beta
        if (eval > alpha):
            alpha = eval

        moves = state.FilterValidMoves(onlyCaptures=True)
        ordered_moves = self.MoveOrdering.OrderMoves(state, moves)

        if len(ordered_moves) > 50:
            ordered_moves = ordered_moves[:50]

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

class tagPVLINE:
    def __init__(self) -> None:
        self.PVLINE = []
        self.numMovesInLine = 15

class SearchDebugInfo:
    def __init__(self):
        self.lastCompletedDepth = 0
        self.moveVal = 0
        self.move = None
        self.eval = 0
        self.isBook = False
        self.numPositionsEvaluated = 0
