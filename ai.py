import random
import time
from evaluation import Evaluate

CHECKMATE = 10 ** 10
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


class ChessAi:
    def __init__(self):
        pass

    def rand_move_ai(self, valid_moves):
        return random.choice(valid_moves)

    def minmax_ai(self, state, returnQueue):
        global next_move, count

        start = time.time()
        next_move = None
        count = 0
        score = self.search(
            state,
            DEPTH,
            -CHECKMATE,
            CHECKMATE,
        )

        print("-------------------------------------------------------------------")
        print("NEXT MOVE:", next_move, count, score)
        print("-------------------------------------------------------------------")

        returnQueue.put(next_move)
        end = time.time()

        print("TIME AI TOOK TO GENERATE NEXT MOVE:", end - start)

    def search(self, state, depth, alpha, beta):

        global next_move, count
        count += 1

        if depth == 0:
            return self.searchAllCaptures(state, alpha, beta)

        validMoves = state.FilterValidMoves()
        if len(validMoves) == 0:
            if state.inCheck():
                return -CHECKMATE
            else:
                return 0

        for move in validMoves:
            state.make_move(move)
            score = -self.search(state, depth - 1, -beta, -alpha)
            state.undo_move()

            if score >= beta:
                return beta

            if alpha < score:
                alpha = score
                if depth == DEPTH:
                    next_move = move
                    print("parsed move:", next_move, score)

        return alpha

    def order_moves(self, state, valid_moves):
        cache = {}
        ordered_dict = {}
        filtered_moves = []

        for move in valid_moves:
            score = 0
            movepiece = move.pieceMoved
            piececapture = move.pieceCaptured

            if piececapture != "--":
                score = 10 * piece_vals[piececapture[1]] - piece_vals[movepiece[1]]

            if move.isPawnPromotion:
                score += piece_vals["Q"]

            state.make_move(move)
            oppMoves = state.FilterValidMoves()
            for oppMove in oppMoves:
                if oppMove.pieceMoved[1] == "p" and oppMove.pieceCaptured != "--":
                    score -= piece_vals[movepiece[1]]
            state.undo_move()

            cache[score] = move

        ordered_dict = dict(sorted(cache.items(), reverse=True))

        for ordered_move in ordered_dict:
            filtered_moves.append(ordered_dict[ordered_move])

        return filtered_moves

    def order_moves_withscore(self, state, valid_moves):
        cache = {}
        ordered_dict = {}
        # capturedPieceValueMultiplier = 1
        # squareControlledByOpponentPawnPenalty = 3.5
        for move in valid_moves:
            state.make_move(move)
            score = self.evaluate(state)
            state.undo_move()

            cache[score] = move

        ordered_dict = dict(sorted(cache.items()))
        return ordered_dict

    def evaluate(self, state):
        evaluation = Evaluate()
        return evaluation.evaluate(state)

        # blackEval = 0
        # whiteEval = 0
        # for row in range(len(state.board)):
        #    for col in range(len(state.board[row])):
        #        sq = state.board[row, col]
        #        if sq != "--":
        #            if sq[1] == "p":
        #                if sq[0] == "w":
        #                    pos_val = piece_map_visualization["wp"][row][col]
        #                    whiteEval += piece_vals[sq[1]] + (pos_val * 0.1)
        #                elif sq[0] == "b":
        #                    pos_val = piece_map_visualization["bp"][row][col]
        #                    blackEval += piece_vals[sq[1]] + (pos_val * 0.1)
        #            else:
        #                if sq[0] == "w":
        #                    pos_val = piece_map_visualization[sq[1]][row][col]
        #                    whiteEval += piece_vals[sq[1]] + (pos_val * 0.1)
        #                if sq[0] == "b":
        #                    pos_val = piece_map_visualization[sq[1]][row][col]
        #                    blackEval += piece_vals[sq[1]] + (pos_val * 0.1)

        # perspective = 1 if (state.whitesturn) else -1
        # evaluation = whiteEval - blackEval
        # print("SCORE:", evaluation)
        # return evaluation * perspective

    def searchAllCaptures(self, state, alpha, beta):
        evaluation = self.evaluate(state)
        if evaluation >= beta:
            return beta

        alpha = max(alpha, evaluation)
        captureMoves = state.FilterValidMoves(onlyCaptures=True)
        ordered_moves = self.order_moves(state, captureMoves)

        for capturemove in ordered_moves:
            state.make_move(capturemove)
            evaluation = -self.searchAllCaptures(state, -beta, -alpha)
            state.undo_move()

            if evaluation >= beta:
                return beta

            alpha = max(alpha, evaluation)

        return alpha


class Test:
    def __init__(self):
        pass

    def testMoveOrdering(self):
        from engine import State

        a = ChessAi()
        e = State()

        ordered_dict = a.order_moves_withscore(e, e.FilterValidMoves())
        filtered_list = []

        for ordered_move in ordered_dict:
            filtered_list.append(ordered_dict[ordered_move])
            print("RAW MOVE:", ordered_move, ordered_dict[ordered_move])

        for move in filtered_list:
            print("FILTERED MOVE:", move)
