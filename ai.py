import numpy as np
import random
import threading
import time

CHECKMATE = 1e8
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

piece_map_visualization = {
    "K": np.array(
        [
            [2, 3, 1, 0, 0, 1, 3, 2],
            [2, 2, 0, 0, 0, 0, 2, 2],
            [-3, -4, -4, -5, -5, -4, -4, -3],
            [-3, -4, -4, -5, -5, -4, -4, -3],
            [-3, -4, -4, -5, -5, -4, -4, -3],
            [-3, -4, -4, -5, -5, -4, -4, -3],
            [2, 2, 0, 0, 0, 0, 2, 2],
            [2, 3, 1, 0, 0, 1, 3, 2],
        ]
    ),
    "Q": np.array(
        [
            [-2, -1, -1, -0.5, -0.5, -1, -1, -2],
            [-1, 0, 0, 0, 0, 0, 0, -1],
            [-1, 0, 0.5, 0.5, 0.5, 0.5, 0, -1],
            [-0.5, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5],
            [-0.5, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5],
            [-1, 0.5, 0.5, 0.5, 0.5, 0.5, 0, -1],
            [-1, 0, 0.5, 0, 0, 0, 0, -1],
            [-2, -1, -1, -0.5, -0.5, -1, -1, -2],
        ]
    ),
    "R": np.array(
        [
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0.5, 1, 1, 1, 1, 1, 1, 0.5],
            [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
            [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
            [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
            [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
            [0.5, 1, 1, 1, 1, 1, 1, 0.5],
            [0, 0, 0, 1, 1, 0, 0, 0],
        ]
    ),
    "B": np.array(
        [
            [-2, -1, -1, -1, -1, -1, -1, -2],
            [-1, 0, 0, 0, 0, 0, 0, -1],
            [-1, 0, 0.5, 1, 1, 0.5, 0, -1],
            [-1, 0.5, 0.5, 1, 1, 0.5, 0.5, -1],
            [-1, 0, 1, 1, 1, 1, 0, -1],
            [-1, 1, 1, 1, 1, 1, 1, -1],
            [-1, 1, 0, 0, 0, 0, 1, -1],
            [-2, -1, -1, -1, -1, -1, -1, -2],
        ]
    ),
    "N": np.array(
        [
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [0, -2, 0, 0, 0, 0, -2, 0],
            [0, 0, 1, 1.5, 1.5, 1, 0, 0],
            [0, 0.5, 1.5, 2, 2, 1.5, 0.5, 0],
            [0, 0, 1.5, 2, 2, 1.5, 0, 0],
            [0, 0.5, 1.5, 2, 2, 1.5, 0.5, 0],
            [0, 1, 0, 0.5, 0.5, 0, 1, 0],
            [-1, -1, -1, -1, -1, -1, -1, -1],
        ]
    ),
    "wp": np.array(
        [
            [7, 8, 8, 8, 8, 8, 8, 7],
            [5, 5, 5, 5, 5, 5, 5, 5],
            [1, 1, 2, 3, 3, 2, 1, 1],
            [0.5, 0.5, 1, 2.5, 2.5, 1, 0.5, 0.5],
            [0, 0, 2, 2, 2, 2, 0, 0],
            [1, 1, 1, 0, 0, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ]
    ),
    "bp": np.array(
        [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 0, 0, 1, 1, 1],
            [0, 0, 2, 2, 2, 2, 0, 0],
            [0.5, 0.5, 1, 2.5, 2.5, 1, 0.5, 0.5],
            [1, 1, 2, 3, 3, 2, 1, 1],
            [5, 5, 5, 5, 5, 5, 5, 5],
            [7, 8, 8, 8, 8, 8, 8, 7],
        ]
    ),
}


class ChessAi:
    def __init__(self):
        pass

    def rand_move_ai(self, valid_moves):
        return random.choice(valid_moves)

    def minmax_ai(self, state, valid_moves, returnQueue):
        global next_move, count

        start = time.time()
        ordered_moves = self.order_moves(state, valid_moves)
        next_move = None
        count = 0
        score = self.search(
            state,
            DEPTH,
            CHECKMATE,
            -CHECKMATE,
            ordered_moves,
            1 if state.whitesturn else -1,
        )

        # self.search(state,valid_moves,DEPTH,-CHECKMATE,CHECKMATE)
        print("-------------------------------------------------------------------")
        print("NEXT MOVE:", next_move, count, score)
        print("-------------------------------------------------------------------")

        returnQueue.put(next_move)
        end = time.time()

        print("TIME AI TOOK TO GENERATE NEXT MOVE:", end - start)

    def search(self, state, depth, beta, alpha, validMoves, turnmultiplier):

        global next_move, count
        count += 1

        if depth == 0 or state.game_over:
            return self.searchAllCaptures(state, alpha, beta)

        max_score = -CHECKMATE
        for move in validMoves:
            state.make_move(move)

            next_moves = state.FilterValidMoves()
            ordered_moves = self.order_moves(state, next_moves)

            score = -self.search(
                state, depth - 1, -alpha, -beta, ordered_moves, -turnmultiplier
            )

            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
                    print("parsed move:", move, score)

            state.undo_move()

            alpha = max(alpha, max_score)
            if alpha >= beta:
                break

        return max_score

    def order_moves(self, state, valid_moves):
        cache = {}
        ordered_dict = {}
        filtered_moves = []

        for move in valid_moves:

            state.make_move(move)
            score = self.evaluate(state)
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
        blackEval = 0
        whiteEval = 0
        for row in range(len(state.board)):
            for col in range(len(state.board[row])):
                sq = state.board[row, col]
                if sq != "--":
                    if sq[1] == "p":
                        if sq[0] == "w":
                            pos_val = piece_map_visualization["wp"][row][col]
                            whiteEval += piece_vals[sq[1]] + (pos_val * 0.1)
                        elif sq[0] == "b":
                            pos_val = piece_map_visualization["bp"][row][col]
                            blackEval += piece_vals[sq[1]] + (pos_val * 0.1)
                    else:
                        if sq[0] == "w":
                            pos_val = piece_map_visualization[sq[1]][row][col]
                            whiteEval += piece_vals[sq[1]] + (pos_val * 0.1)
                        if sq[0] == "b":
                            pos_val = piece_map_visualization[sq[1]][row][col]
                            blackEval += piece_vals[sq[1]] + (pos_val * 0.1)

        perspective = 1 if (state.whitesturn) else -1
        evaluation = whiteEval - blackEval
        # print("SCORE:", evaluation)
        return evaluation * perspective

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

        ordered_dict = a.order_moves_withscore(
            e, e.FilterValidMoves()
        )
        filtered_list = []

        for ordered_move in ordered_dict:
            filtered_list.append(ordered_dict[ordered_move])
            print("RAW MOVE:", ordered_move, ordered_dict[ordered_move])

        for move in filtered_list:
            print("FILTERED MOVE:", move)
