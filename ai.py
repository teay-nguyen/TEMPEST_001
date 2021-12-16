import numpy as np
import random

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 4


class ChessAi:
    def __init__(self):
        pass

    def rand_move_ai(self, valid_moves):
        return (random.choice(valid_moves))

    '''
    def greedy_alg_norec(self, state, valid_moves):
        turn_mult = 1 if state.whitesturn else -1

        opp_minmax_score = CHECKMATE
        best_plr_move = None
        random.shuffle(valid_moves)

        for plr_move in valid_moves:
            state.make_move(plr_move)
            opponentMoves = state.FilterValidMoves()

            if state.stalemate:
                oppMaxScore = STALEMATE
            elif state.checkmate:
                oppMaxScore = -CHECKMATE
            else:
                oppMaxScore = -CHECKMATE
                for oppMove in opponentMoves:
                    state.make_move(oppMove)
                    state.FilterValidMoves()
                    if state.checkmate:
                        score = CHECKMATE
                    elif state.stalemate:
                        score = STALEMATE
                    else:
                        score = -turn_mult * self.evaluate(state.board)
                    if score > oppMaxScore:
                        oppMaxScore = score
                    state.undo_move()

            if opp_minmax_score > oppMaxScore:
                opp_minmax_score = oppMaxScore
                best_plr_move = plr_move
            state.undo_move()

        return best_plr_move
    '''

    def minmax_ai(self, state, valid_moves, returnQueue):
        global next_move,count

        next_move = None
        count = 0
        random.shuffle(valid_moves)
        self.neg_ap(state, DEPTH, CHECKMATE, -CHECKMATE,
                                        valid_moves, 1 if state.whitesturn else -1, count)

        print(next_move, count)
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

    '''
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
    '''

    def neg_ap(self, state, depth, beta, alpha, validMoves, turnmultiplier, count):
        random.shuffle(validMoves)
        global piece_vals
        piece_vals = {
            'K': 0,
            'Q': 10,
            'R': 5,
            'B': 3,
            'N': 3,
            'p': 1,
        }

        global next_move
        count += 1

        if depth == 0:
            return turnmultiplier * self.scoreboard(state)

        max_score = -CHECKMATE
        for move in validMoves:
            state.make_move(move)
            next_moves = state.FilterValidMoves()
            score = -self.neg_ap(state, depth-1, -beta,-alpha, next_moves, -turnmultiplier, count)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            state.undo_move()
            if max_score > alpha:
                alpha = max_score
            if alpha >= beta:
                break

        return max_score

    '''
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
    '''

    def scoreboard(self, state):
        if state.checkmate:
            if state.whitesturn:
                return -CHECKMATE
            else:
                return CHECKMATE
        elif state.stalemate:
            return STALEMATE

        score = 0
        for row in range(len(state.board)):
            for col in range(len(state.board[row])):
                square = state.board[row, col]
                if square[0] == 'w':
                    score += piece_vals[square[1]]
                elif square[0] == 'b':
                    score -= piece_vals[square[1]]

        return score

    '''
    def evaluate(self, board):
        score = 0
        for row in board:
            for square in row:
                if square[0] == 'w':
                    score += piece_val[square[1]]
                elif square[0] == 'b':
                    score -= piece_val[square[1]]

        return score

    '''
