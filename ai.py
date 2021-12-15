
import random


class ChessAi:
    def __init__(self):
        pass

    def rand_move_ai(self, valid_moves):
        return valid_moves[random.randint(0, len(valid_moves)-1)]

    def best_move_ai(self, valid_moves):
        pass
