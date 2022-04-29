
from data import *
from defs import *

def eval_position(board: list, side: int) -> int:
    score = 0
    for sq in range(BOARD_SQ_NUM):
        if not (sq & 0x88):
            piece = board[sq]
            score += piece_val[piece]

    return score if side else -score
