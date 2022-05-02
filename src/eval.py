
from data import *
from defs import *

PAWN = 0
KNIGHT = 1
BISHOP = 2
ROOK = 3
QUEEN = 4
KING = 5

# score to determine the game phase
def get_game_phase_score(pceNum:list) -> int:
    wp_scores, bp_scores = 0, 0

    for piece in range(N, K): wp_scores += pceNum[piece] * piece_val[phases['opening']][piece]
    for piece in range(n, k): bp_scores += pceNum[piece] * -piece_val[phases['opening']][piece]

    return wp_scores + bp_scores

# the good stuff :)
def evaluate(board: list, side: int, pceNum: list) -> int:
    game_phase_score:int = get_game_phase_score(pceNum)
    game_phase:int = -1

    if game_phase_score > OPENING_PHASE_SCORE: game_phase = phases['opening']
    elif game_phase_score < ENDGAME_PHASE_SCORE: game_phase = phases['endgame']
    else: game_phase = phases['midgame']

    score:int = 0; score_opening:int = 0; score_endgame:int = 0

    for sq in range(len(board)):
        if not (sq & 0x88):
            piece:int = board[sq]
            if piece == P:
                score_opening += positional_score[phases['opening']][PAWN][sq]
                score_endgame += positional_score[phases['endgame']][PAWN][sq]
            elif piece == N:
                score_opening += positional_score[phases['opening']][KNIGHT][sq]
                score_endgame += positional_score[phases['endgame']][KNIGHT][sq]
            elif piece == B:
                score_opening += positional_score[phases['opening']][BISHOP][sq]
                score_endgame += positional_score[phases['endgame']][BISHOP][sq]
            elif piece == R:
                score_opening += positional_score[phases['opening']][ROOK][sq]
                score_endgame += positional_score[phases['endgame']][ROOK][sq]
            elif piece == Q:
                score_opening += positional_score[phases['opening']][QUEEN][sq]
                score_endgame += positional_score[phases['endgame']][QUEEN][sq]
            elif piece == K:
                score_opening += positional_score[phases['opening']][KING][sq]
                score_endgame += positional_score[phases['endgame']][KING][sq]
            elif piece == p:
                score_opening -= positional_score[phases['opening']][PAWN][mirror_board[sq]]
                score_endgame -= positional_score[phases['endgame']][PAWN][mirror_board[sq]]
            elif piece == n:
                score_opening -= positional_score[phases['opening']][KNIGHT][mirror_board[sq]]
                score_endgame -= positional_score[phases['endgame']][KNIGHT][mirror_board[sq]]
            elif piece == b:
                score_opening -= positional_score[phases['opening']][BISHOP][mirror_board[sq]]
                score_endgame -= positional_score[phases['endgame']][BISHOP][mirror_board[sq]]
            elif piece == r:
                score_opening -= positional_score[phases['opening']][ROOK][mirror_board[sq]]
                score_endgame -= positional_score[phases['endgame']][ROOK][mirror_board[sq]]
            elif piece == q:
                score_opening -= positional_score[phases['opening']][QUEEN][mirror_board[sq]]
                score_endgame -= positional_score[phases['endgame']][QUEEN][mirror_board[sq]]
            elif piece == k:
                score_opening -= positional_score[phases['opening']][KING][mirror_board[sq]]
                score_endgame -= positional_score[phases['endgame']][KING][mirror_board[sq]]

    if (game_phase == phases['midgame']): score = (score_opening * game_phase_score + score_endgame * (OPENING_PHASE_SCORE - game_phase_score)) / OPENING_PHASE_SCORE
    elif game_phase == phases['opening']: score = score_opening
    elif game_phase == phases['endgame']: score = score_endgame

    game_phase_res:str = ''
    if not game_phase:
        game_phase_res = 'OPENING'
    elif game_phase == 1:
        game_phase_res = 'ENDGAME'
    elif game_phase == 2:
        game_phase_res = 'MIDDLEGAME'

    print(f'  [GAME PHASE]: {game_phase_res}')

    return score if side else (score * -1)
