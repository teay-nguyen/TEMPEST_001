from random import choice
from time import time
from evaluation import Evaluate
import time
from MoveOrdering import MoveOrdering


class DepthLite1():

    def __init__(self):
        self.count = 0
        self.bestMoveInIteration = None
        self.bestEvalInIteration = 0
        self.bestMoveFound = None
        self.bestEvalFound = 0
        self.useIterativeDeepening = True
        self.DefaultDepth = 2
        self.POSITIVE_INF = 999999999
        self.NEGATIVE_INF = -999999999
        self.immediateMateScore = 100000
        self.numNodes = 0
        self.numCutoffs = 0
        self.abortSearch = False
        self.LowPerformanceMode = True
        self.searchDebugInfo = None

    def random_move(self, state):
        moves = state.FilterValidMoves()
        return choice(moves)

    def startSearch(self, state, rQueue):
        self.bestMoveFound = self.bestMoveInIteration = None
        self.bestEvalFound = self.numCutoffs = self.bestEvalInIteration = 0
        self.abortSearch = False
        self.searchDebugInfo = SearchDebugInfo()

        start = time.time()
        currentIterativeSearchDepth = 0
        highPerformantDepth = 4
        lowPerformantDepth = self.DefaultDepth

        if self.useIterativeDeepening:
            targetDepth = lowPerformantDepth if self.LowPerformanceMode else highPerformantDepth

            for depth in range(1, targetDepth + 1):
                print('Searching Depth:', depth)
                self.Search(state, depth, self.NEGATIVE_INF,
                            self.POSITIVE_INF, 0)

                searchTime = time.time()
                if (searchTime - start) > 4 or self.abortSearch:
                    self.bestMoveFound = self.bestMoveInIteration
                    self.bestEvalFound = self.bestEvalInIteration
                    print(
                        'TIME LIMIT EXCEEDED OR ABORT SEARCH ACTIVATED! EXITING SEARCH:', (searchTime - start))
                    break
                else:
                    currentIterativeSearchDepth = depth
                    self.bestMoveFound = self.bestMoveInIteration
                    self.bestEvalFound = self.bestEvalInIteration

                    self.searchDebugInfo.lastCompletedDepth = depth
                    self.searchDebugInfo.eval = self.bestEvalFound
                    self.searchDebugInfo.moveVal = 0

                    try:
                        self.searchDebugInfo.move = self.bestMoveFound.getChessNotation(
                            True)
                    except Exception:
                        pass

                    if self.isMateScore(self.bestEvalFound):
                        print('MATE FOUND, EXITING SEARCH')
                        break
        else:
            targetDepth = lowPerformantDepth if self.LowPerformanceMode else highPerformantDepth
            self.Search(state, targetDepth, self.NEGATIVE_INF,
                        self.POSITIVE_INF, 0)
            self.bestMoveFound = self.bestMoveInIteration
            self.bestEvalFound = self.bestEvalInIteration

        print()
        print('---------------------------------------')
        print('NEXT MOVE:', self.bestMoveFound, self.count, self.bestEvalFound)
        print('---------------------------------------\n')

        end = time.time()
        print('TIME TOOK TO GENERATE NEXT MOVE:', end - start)

        rQueue.put(self.bestMoveFound)

    def GetSearchResult(self):
        return (self.bestMoveFound, self.bestEvalFound)

    def EndSearch(self):
        self.abortSearch = True

    def Search(self, state, depth, alpha, beta, plyFromRoot):
        if (self.abortSearch):
            return 0

        if (plyFromRoot > 0):
            alpha = max(alpha, -self.immediateMateScore + plyFromRoot)
            beta = min(beta, self.immediateMateScore - plyFromRoot)
            if alpha >= beta:
                return alpha

        self.count += 1
        MoveOrder = MoveOrdering()
        moves = state.FilterValidMoves()
        ordered_moves = MoveOrder.OrderMoves(state, moves)

        if depth == 0:
            eval = self.QuiescenceSearch(state, alpha, beta)
            return eval

        if len(moves) == 0:
            if state.inCheck():
                mateScore = self.immediateMateScore - plyFromRoot
                return -mateScore
            else:
                return 0

        bestMoveInPosition = None

        for move in ordered_moves:
            state.make_move(move)
            eval = -self.Search(state, depth - 1, -
                                beta, -alpha, plyFromRoot + 1)
            state.undo_move()
            self.numNodes += 1

            if (eval >= beta):
                self.numCutoffs += 1
                return beta

            if (eval > alpha):
                bestMoveInPosition = move
                alpha = eval

                if plyFromRoot == 0:
                    print('New Best Move Found:', move, eval)
                    self.bestEvalInIteration = eval
                    self.bestMoveInIteration = move

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
            state.make_move(move)
            eval = -self.QuiescenceSearch(state, -beta, -alpha)
            state.undo_move()

            if (eval >= beta):
                self.numCutoffs += 1
                return beta
            if (eval > alpha):
                alpha = eval

        return alpha

    def isMateScore(self, score):
        maxMateDepth = 1000
        return abs(score) > (self.immediateMateScore - maxMateDepth)


class SearchDebugInfo:
    def __init__(self):
        self.lastCompletedDepth = 0
        self.moveVal = 0
        self.move = None
        self.eval = 0
        self.isBook = False
        self.numPositionsEvaluated = 0
