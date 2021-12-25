from random import choice, randrange
from time import time
from evaluation import Evaluate
import numpy as np

CHECKMATE = np.inf
STALEMATE = 0
DEPTH = 2

piece_vals = {
    "K": 0,
    "Q": 10,
    "R": 5,
    "B": 3,
    "N": 3,
    "p": 1,
}


def random_line(afile):
    line = next(afile)
    for num, aline in enumerate(afile, 2):
        if randrange(num):
            continue
        line = aline
    return line


class ChessAi:

    def __init__(self):
        self.count = 0
        self.bestMoveInIteration = None
        self.bestEvalInIteration = 0
        self.bestMoveFound = None
        self.bestEvalFound = 0

    def rand_move_ai(self, valid_moves):
        return choice(valid_moves)

    def startSearch(self, state, returnQueue):
        start, self.bestMoveInIteration, self.bestEvalInIteration, self.count, score = time(), None, 0, 0, 0
        self.bestMoveFound = None
        self.bestEvalFound = 0

        for idx in range(DEPTH):
            currdepth = idx + 1
            score = self.search(
                state,
                currdepth,
                -CHECKMATE,
                CHECKMATE,
            )

            search_time = time()
            if (search_time - start) > 4:
                print('TIME LIMIT EXCEEDED! BREAKING OUT OF LOOP:',
                      (search_time - start))
                break

        self.bestMoveFound = self.bestMoveInIteration
        self.bestEvalFound = self.bestEvalInIteration

        print()
        print("-------------------------------------------------------------------")
        print("NEXT MOVE:", self.bestMoveFound, self.count, self.bestEvalFound)
        print("-------------------------------------------------------------------\n")

        returnQueue.put(self.bestMoveInIteration)
        end = time()

        print("TIME AI TOOK TO GENERATE NEXT MOVE:", end - start)

    def search(self, state, depth, alpha, beta):

        self.count += 1

        if depth == 0:
            return self.quiesSearch(state, alpha, beta)

        validMoves = state.FilterValidMoves()
        ordered_moves = self.order_moves(state, validMoves)

        if len(validMoves) == 0:
            return -CHECKMATE if state.inCheck() else STALEMATE

        bestMoveThisPosition = None

        for move in ordered_moves:
            state.make_move(move)
            score = -self.search(state, depth - 1, -beta, -alpha)
            state.undo_move()

            if score >= beta:
                return beta

            if score > alpha:
                alpha = score
                bestMoveThisPosition = move
                if depth == DEPTH:
                    self.bestMoveInIteration = move
                    self.bestEvalInIteration = score
                    print("parsed move:", self.bestMoveInIteration, score)

        return alpha

    def order_moves(self, state, valid_moves):
        cache = {}

        for move in valid_moves:

            score = 0
            movepiece = move.pieceMoved
            piececapture = move.pieceCaptured

            if piececapture != "--":
                score += (piece_vals[piececapture[1]] -
                          piece_vals[movepiece[1]])

            if move.isPawnPromotion:
                score += piece_vals["Q"]

            oppPawnAttackMap = state.oppPawnAttackMap
            moveendSquare = (move.endRow, move.endCol)

            if moveendSquare in oppPawnAttackMap:
                score -= piece_vals[movepiece[1]]

            cache[score] = move

        ordered_dict = dict(sorted(cache.items(), reverse=True))
        filtered_moves = [ordered_dict[ordered_move]
                          for ordered_move in ordered_dict]

        return filtered_moves

    def evaluate(self, state):
        evaluation = Evaluate()
        return evaluation.evaluate(state)

    def quiesSearch(self, state, alpha, beta):
        evaluation = self.evaluate(state)
        if evaluation >= beta:
            return beta
        if evaluation > alpha:
            alpha = evaluation

        captureMoves = state.FilterValidMoves(onlyCaptures=True)
        ordered_moves = self.order_moves(state, captureMoves)

        for capturemove in ordered_moves:
            state.make_move(capturemove)
            evaluation = -self.quiesSearch(state, -beta, -alpha)
            state.undo_move()

            if evaluation >= beta:
                return beta

            if evaluation > alpha:
                alpha = evaluation

        return alpha
