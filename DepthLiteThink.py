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
        self.NEGATIVE_INF = -self.POSITIVE_INF
        self.numNodes = 0
        self.abortSearch = False

    def random_move(self, state):
        moves = state.FilterValidMoves()
        return choice(moves)

    def startSearch(self, state, rQueue):
        self.bestMoveFound = self.bestMoveInIteration = None
        self.bestEvalFound = self.bestEvalInIteration = 0
        self.abortSearch = False
        MoveOrder = MoveOrdering()
        moves = state.FilterValidMoves()
        start = time.time()

        orderedMoves = MoveOrder.OrderMoves(state, moves)

        if self.useIterativeDeepening:
            for _ in range(self.DefaultDepth):
                print('Searching Depth:', _ + 1)
                depth = _ + 1
                eval = self.Search(
                    state, depth, self.NEGATIVE_INF, self.POSITIVE_INF, orderedMoves, 0)

                searchTime = time.time()
                if (searchTime - start) > 4 or self.abortSearch:
                    self.bestMoveFound = self.bestMoveInIteration
                    self.bestEvalFound = self.bestEvalInIteration
                    print('TIME LIMIT EXCEEDED! EXITING SEARCH:',
                          (searchTime - start))
                    break
                else:
                    self.bestMoveFound = self.bestMoveInIteration
                    self.bestEvalFound = self.bestEvalInIteration

                    if self.bestEvalFound >= self.POSITIVE_INF:
                        print('MATE FOUND, EXITING SEARCH')
                        break
        else:
            eval = self.Search(state, self.DefaultDepth,
                               self.NEGATIVE_INF, self.POSITIVE_INF, orderedMoves, 0)
            self.bestMoveFound = self.bestMoveInIteration
            self.bestEvalFound = self.bestEvalInIteration

        print()
        print('---------------------------------------')
        print('NEXT MOVE:', self.bestMoveFound, self.count, self.bestEvalFound)
        print('---------------------------------------\n')

        end = time.time()
        print('TIME TOOK TO GENERATE NEXT MOVE:', end - start)

        rQueue.put(self.bestMoveFound)

    def Search(self, state, currentDepth, alpha, beta, moves, plyFromRoot):
        self.count += 1
        MoveOrder = MoveOrdering()
        if currentDepth == 0:
            #evaluation = Evaluate()
            return self.QuiescenceSearch(state, alpha, beta)

        if len(moves) == 0:
            if state.inCheck():
                return self.NEGATIVE_INF
            return 0

        bestMoveInPosition = None

        for move in moves:
            state.make_move(move)
            oppMoves = state.FilterValidMoves()
            orderedMoves = MoveOrder.OrderMoves(state, oppMoves)
            eval = -self.Search(state, currentDepth -
                                1, -beta, -alpha, orderedMoves, plyFromRoot + 1)
            state.undo_move()
            self.numNodes += 1

            if (eval >= beta):
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
        moves = state.FilterValidMoves(onlyCaptures=True)
        ordered_moves = OrderClass.OrderMoves(state, moves)

        if (eval >= beta):
            return beta

        alpha = max(eval, alpha)

        for move in ordered_moves:
            state.make_move(move)
            eval = -self.QuiescenceSearch(state, -beta, -alpha)
            state.undo_move()

            if (eval >= beta):
                return beta

            alpha = max(eval, alpha)

        return alpha
