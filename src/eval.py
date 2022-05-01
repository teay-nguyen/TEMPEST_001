
from data import *
from defs import *

def get_game_phase_score(pceNum:list) -> int:
    wp_scores, bp_scores = 0, 0

    for piece in range(N, Q+1):
        wp_scores += pceNum[piece] * piece_val[phases['opening']][piece]

    for piece in range(n, q+1):
        bp_scores += pceNum[piece] * piece_val[phases['opening']][piece]

    return wp_scores + bp_scores

def evaluate(board: list, side: int, pceNum: list) -> int:
    game_phase_score = get_game_phase_score(pceNum)
    game_phase = -1

    if game_phase_score > opening_phase_score: game_phase = phases['opening']

    score = 0
    for sq in range(BOARD_SQ_NUM):
        if not (sq & 0x88):
            piece = board[sq]
            score += piece_val[piece]

    return score if side else -score
