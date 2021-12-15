
import random

piece_val = {'K': 0, 'Q': 10, 'R': 5, 'B': 3, 'N': 3, 'p': 1}
CHECKMATE = 100000
STALEMATE = 0
DEPTH = 2


class ChessAi:
    def __init__(self):
        pass

    def rand_move_ai(self, valid_moves):
        return valid_moves[random.randint(0, len(valid_moves)-1)]
        # return random.choice(valid_moves)

    def best_move_ai(self, state, valid_moves):
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

    def minmax_ai(self, state, valid_moves):
        global next_move

        next_move = None
        self.minmax(state, valid_moves, DEPTH, state.whitesturn)

        return next_move

    def minmax(self, state, valid_moves, depth, whitesturn):
        global next_move
        if depth == 0:
            return self.evaluate(state.board)

        if whitesturn:
            maxScore = -CHECKMATE
            for move in valid_moves:
                state.make_move(move)
                next_moves = state.FilterValidMoves()
                score = self.minmax(state, valid_moves, depth-1, False)
                if score > maxScore:
                    maxScore = score
                    if depth == DEPTH:
                        next_move = move

                state.undo_move()

            return maxScore
        else:
            minScore = CHECKMATE
            for move in valid_moves:
                state.make_move(move)
                next_moves = state.FilterValidMoves()
                score = self.minmax(state, valid_moves, depth-1, True)
                if score < minScore:
                    minScore = score
                    if depth == DEPTH:
                        next_move = move

                state.undo_move()

            return minScore

    def scoreboard(self, state):
        if state.checkmate:
            if state.whitesturn:
                return -CHECKMATE
            else:
                return CHECKMATE
        elif state.stalemate:
            return STALEMATE

        score = 0
        for row in state.board:
            for square in row:
                if square[0] == 'w':
                    score += piece_val[square[1]]
                elif square[0] == 'b':
                    score -= piece_val[square[1]]

        return score

    def evaluate(self, board):
        score = 0
        for row in board:
            for square in row:
                if square[0] == 'w':
                    score += piece_val[square[1]]
                elif square[0] == 'b':
                    score -= piece_val[square[1]]

        return score
