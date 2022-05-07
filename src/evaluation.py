'''

    TEMPEST_001, a didactic chess engine written in Python
    Copyright (C) 2022  Terry Nguyen (PyPioneer author)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''

#!/usr/bin/env pypy3 -u
# -*- coding: utf-8 -*-

# imports
from data import SUPPORTED_BONUS, DOUBLED_PENALTY,piece_val, phases, BISHOP_PAIR_BONUS, KNIGHT_PAIR_BONUS, ROOK_PAIR_BONUS,\
                 OPENING_PHASE_SCORE, ENDGAME_PHASE_SCORE, positional_score, mirror_board
from defs import p, n, b, r, q, k, P, N, B, R, Q, K
from transposition import Transposition, NO_HASH_ENTRY

# initialize the transposition table
tt = Transposition()
tt.tteval_setsize(0x10F447)

# predefined variables so code can be more readable
PAWN:int = 0; KNIGHT:int = 1; BISHOP:int = 2; ROOK:int = 3; QUEEN:int = 4; KING:int = 5

def eval_pawn(board, sq, side) -> float:
    # validate if piece is pawn on the given side or not
    if (board[sq] != P) if side else (board[sq] != p): return 0

    # define vars
    score:int = 0

    # increment these variables as we move up the board
    increment_step_white:int = sq - 16
    increment_step_black:int = sq + 16

    # calc pawn score based on doubled pawns and supported pawns
    if side:
        if (board[sq + 15] == P and 0 <= (sq + 15) <= 127) or (board[sq + 17] == P and 0 <= (sq + 17) <= 127):
            score += SUPPORTED_BONUS
        while not (increment_step_white & 0x88) and 0 <= increment_step_white <= 127:
            if board[increment_step_white] == P: score -= DOUBLED_PENALTY
            increment_step_white -= 16
    else:
        if (board[sq - 15] == p and 0 <= (sq - 15) <= 127) or (board[sq - 17] == p and 0 <= (sq - 17) <= 127):
            score += SUPPORTED_BONUS
        while not (increment_step_black & 0x88) and 0 <= increment_step_black <= 127:
            if board[increment_step_black] == p: score -= DOUBLED_PENALTY
            increment_step_black += 16

    # return the scaled score
    return (score*2)/1.2

# score to determine the game phase
def get_game_phase_score(pceNum:list) -> int:
    # define the variables
    wp_scores:int = 0; bp_scores:int = 0

    # loop through pieces and add them to the variables
    for piece in range(N, K): wp_scores += pceNum[piece] * piece_val[phases['opening']][piece]
    for piece in range(n, k): bp_scores += pceNum[piece] * -piece_val[phases['opening']][piece]

    # return the total amount of material, minus the pawns
    return wp_scores + bp_scores

# main driver
def evaluate(board: list, side: int, pceNum: list, hashkey: int) -> float:

    # probe the table for any available entries
    tt_score:int = tt.tteval_probe(hashkey)
    if tt_score != NO_HASH_ENTRY: return tt_score

    # fetch game phase score to determine game phase
    game_phase_score:int = get_game_phase_score(pceNum)

    # init game phase variable
    game_phase:int = -1

    # specify game phase var based on game phase score
    if game_phase_score > OPENING_PHASE_SCORE: game_phase = phases['opening']
    elif game_phase_score < ENDGAME_PHASE_SCORE: game_phase = phases['endgame']
    else: game_phase = phases['midgame']

    # define score variables
    score:float = 0; score_opening:float = 0; score_endgame:float = 0

    # pair bonuses
    if pceNum[B] > 1:
        score_opening += BISHOP_PAIR_BONUS
        score_endgame += BISHOP_PAIR_BONUS

    if pceNum[b] > 1:
        score_opening -= BISHOP_PAIR_BONUS
        score_endgame -= BISHOP_PAIR_BONUS

    if pceNum[N] > 1:
        score_opening += KNIGHT_PAIR_BONUS
        score_endgame += KNIGHT_PAIR_BONUS

    if pceNum[n] > 1:
        score_opening -= KNIGHT_PAIR_BONUS
        score_endgame -= KNIGHT_PAIR_BONUS

    if pceNum[R] > 1:
        score_opening += ROOK_PAIR_BONUS
        score_endgame += ROOK_PAIR_BONUS

    if pceNum[r] > 1:
        score_opening -= ROOK_PAIR_BONUS
        score_endgame -= ROOK_PAIR_BONUS

    # tedious stuff right here
    for sq in range(len(board)):
        if not (sq & 0x88):
            # define the piece
            piece:int = board[sq]

            # material count
            score_opening += piece_val[phases['opening']][piece]
            score_endgame += piece_val[phases['endgame']][piece]

            # piece square table calculating
            if piece == P:
                score_opening += positional_score[phases['opening']][PAWN][sq]
                score_endgame += positional_score[phases['endgame']][PAWN][sq]
                pawn_eval = eval_pawn(board, sq, 1)
                score_opening += pawn_eval
                score_endgame += pawn_eval
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
                pawn_eval = eval_pawn(board, sq, 0)
                score_opening -= pawn_eval
                score_endgame -= pawn_eval
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

    # determine the final score based on game phase
    # my nvim lsp keep throwing errors this things a nuisance, i need the exact float/value because better move ordering equals better playing strength
    if game_phase == phases['midgame']:
        try: score = (score_opening * game_phase_score + score_endgame * (OPENING_PHASE_SCORE - game_phase_score)) / OPENING_PHASE_SCORE
        except: score = 0
    elif game_phase == phases['opening']: score = round(float(score_opening), 2)
    elif game_phase == phases['endgame']: score = round(float(score_endgame), 2)

    # change the score based on stm, required on the negamax framework
    score = score if side else -score

    # store the score in the tt table in case of encountering this position again
    tt.tteval_save(score, hashkey)

    # return the score
    return score
