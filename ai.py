import numpy as np
import random

CHECKMATE = 1e6
STALEMATE = 0
DEPTH = 3

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
            [-3, -4, -4, -5, -5, -4, -4, -3],
            [-3, -4, -4, -5, -5, -4, -4, -3],
            [-3, -4, -4, -5, -5, -4, -4, -3],
            [-3, -4, -4, -5, -5, -4, -4, -3],
            [-2, -3, -3, -4, -4, -3, -3, -2],
            [-1, -2, -2, -2, -2, -2, -2, -1],
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
            [0, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5],
            [-1, 0.5, 0.5, 0.5, 0.5, 0.5, 0, -1],
            [-1, 0, 0.5, 0, 0, 0, 0, -1],
            [-2, -1, -1, -0.5, -0.5, -1, -1, -2],
        ]
    ),
    "R": np.array(
        [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0.5, 1, 1, 1, 1, 1, 1, 0.5],
            [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
            [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
            [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
            [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
            [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
            [0, 0, 0, 0.5, 0.5, 0, 0, 0],
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
            [-1, 0.5, 0, 0, 0, 0, 0.5, -1],
            [-2, -1, -1, -1, -1, -1, -1, -2],
        ]
    ),
    "N": np.array(
        [
            [-5, -4, -3, -3, -3, -3, -4, -5],
            [-4, -2, 0, 0, 0, 0, -2, -4],
            [-3, 0, 1, 1.5, 1.5, 1, 0, -3],
            [-3, 0.5, 1.5, 2, 2, 1.5, 0.5, -3],
            [-3, 0, 1.5, 2, 2, 1.5, 0, -3],
            [-3, 0.5, 1.5, 2, 2, 1.5, 0.5, -3],
            [-4, -2, 0, 0.5, 0.5, 0, -2, -4],
            [-5, -4, -3, -3, -3, -3, -4, -5],
        ]
    ),
    "p": np.array(
        [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [5, 5, 5, 5, 5, 5, 5, 5],
            [1, 1, 2, 3, 3, 4, 1, 1],
            [0.5, 0.5, 1, 2.5, 2.5, 1, 0.5, 0.5],
            [0, 0, 0, 2, 2, 0, 0, 0],
            [0.5, -0.5, -1, 0, 0, -1, -0.5, 0.5],
            [0.5, 1, 1, -2, -2, 1, 1, 0.5],
            [0, 0, 0, 0, 0, 0, 0, 0],
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

        random.shuffle(valid_moves)
        next_move = None
        count = 0
        score = self.neg_ap(
            state,
            DEPTH,
            CHECKMATE,
            -CHECKMATE,
            valid_moves,
            1 if state.whitesturn else -1,
        )

        # self.search(state,valid_moves,DEPTH,-CHECKMATE,CHECKMATE)
        print(next_move, count, score)
        returnQueue.put(next_move)

    # def minmax(self, state, valid_moves, depth, whitesturn):
    #     global next_move
    #     if depth == 0:
    #         return self.evaluate(state.board)

    #     if whitesturn:
    #         maxScore = -CHECKMATE
    #         for move in valid_moves:
    #             state.make_move(move)
    #             next_moves = state.FilterValidMoves()
    #             score = self.minmax(state, next_moves, depth-1, False)
    #             if score > maxScore:
    #                 maxScore = score
    #                 if depth == DEPTH:
    #                     next_move = move

    #             state.undo_move()

    #         return maxScore
    #     else:
    #         minScore = CHECKMATE
    #         for move in valid_moves:
    #             state.make_move(move)
    #             next_moves = state.FilterValidMoves()
    #             score = self.minmax(state, next_moves, depth-1, True)
    #             if score < minScore:
    #                 minScore = score
    #                 if depth == DEPTH:
    #                     next_move = move

    #             state.undo_move()

    #         return minScore

    """
    def negamax(self, state, valid_moves, depth, turn_mult):
        global next_move, count

        count += 1
        random.shuffle(valid_moves)
        if depth == 0:
            return turn_mult*self.scoreboard(state)

        maxScore = -CHECKMATE
        for move in valid_moves:
            state.make_move(move)

            next_moves = state.FilterValidMoves()
            score = -self.negamax(state, next_moves, depth-1, -turn_mult)

            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    next_move = move

            state.undo_move()

        return maxScore
    """

    def neg_ap(self, state, depth, beta, alpha, validMoves, turnmultiplier):

        global next_move,count
        random.shuffle(validMoves)
        count += 1

        if depth == 0:
            return self.evaluate(state)

        max_score = -CHECKMATE
        for move in validMoves:
            #print(f"parsing move: {move}")
            state.make_move(move)
            next_moves = state.FilterValidMoves()
            score = -self.neg_ap(
                state, depth - 1, -alpha, -beta, next_moves, -turnmultiplier
            )
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move

            state.undo_move()
            alpha = max(alpha,max_score)

            if alpha >= beta:
                break

        return max_score

    """
    def ap_proto(self, state, moveList, depth, alpha, beta):
        global next_move, count

        count += 1
        if depth == 0:
            return self.scoreboard(state)

        for move in moveList:
            state.make_move(move)
            val = -self.ap_proto(state, state.FilterValidMoves(),
                                 depth-1, -alpha, -beta)
            state.undo_move()
            if val >= beta:
                return beta

            elif val > alpha:
                alpha = val
                next_move = move

        return alpha
    """

    """
    def search(self, state, valid_moves, depth, alpha, beta):
        global next_move
        if depth == 0:
            return self.evaluate(state.board)

        if state.checkmate:
            if state.whitesturn:
                return -CHECKMATE
            else:
                return CHECKMATE
        elif state.stalemate:
            return 0

        for move in valid_moves:
            state.make_move(move)
            next_moves = state.FilterValidMoves()
            evaluation = -self.search(state, next_moves, depth - 1, -beta, -alpha)
            state.undo_move()

            if evaluation >= beta:
                return beta

            # alpha = max(alpha,evaluation)
            if alpha < evaluation:
                alpha = evaluation
                next_move = move

        return alpha
    """

    def order_moves(self, state, valid_moves):
        ordered_moves = []
        for move in valid_moves:
            movescoreguess = 0
            movepiecetype = state.board[move.startRow, move.startCol]
            capturepiecetype = state.board[move.endRow, move.endCol]

            if capturepiecetype != "--":
                movescoreguess = (
                    piece_vals[capturepiecetype[1]] - piece_vals[movepiecetype[1]]
                )

            if move.isPawnPromotion:
                movescoreguess += piece_vals["Q"]

            state.whitesturn = not state.whitesturn
            oppMoves = state.FilterValidMoves()
            state.whitesturn = not state.whitesturn

            if move in oppMoves:
                movescoreguess -= piece_vals[movepiecetype[1]]

            ordered_moves.append(movescoreguess)

        return ordered_moves

    def evaluate(self, state):
        score = 0
        for row in range(len(state.board)):
            for col in range(len(state.board[row])):
                sq = state.board[row, col]

                if sq != "--":

                    #print(f"Position value: {pos_val*.1}")

                    if sq[0] == "w":
                        pos_val = piece_map_visualization[sq[1]][row][col]
                        score += piece_vals[sq[1]] + pos_val * 0.1
                    if sq[0] == "b":
                        reverse_map = np.flipud(piece_map_visualization[sq[1]])
                        pos_val = reverse_map[row][col]
                        score -= piece_vals[sq[1]] + pos_val * 0.1

        return score
