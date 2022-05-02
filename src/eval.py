
from data import *
from defs import *

# predefined variables so code can be more readable
PAWN:int = 0; KNIGHT:int = 1; BISHOP:int = 2; ROOK:int = 3; QUEEN:int = 4; KING:int = 5

# score to determine the game phase
def get_game_phase_score(pceNum:list) -> int:
    # define the variables
    wp_scores:int = 0; bp_scores:int = 0

    print()

    # loop through pieces and add them to the variables
    for piece in range(N, K):
        wp_scores += pceNum[piece] * piece_val[phases['opening']][piece]
        print(f'  [White {int_pieces[piece]}]: {pceNum[piece] * piece_val[phases["opening"]][piece]}')
    for piece in range(n, k):
        bp_scores += pceNum[piece] * -piece_val[phases['opening']][piece]
        print(f'  [Black {int_pieces[piece]}]: {pceNum[piece] * -piece_val[phases["opening"]][piece]}')

    print(f'  [WHITE MATERIAL]: {wp_scores}')
    print(f'  [BLACK MATERIAL]: {bp_scores}\n')

    # return the total amount of material, minus the pawns
    return (wp_scores + bp_scores)

# the good stuff :)
def evaluate(board: list, side: int, pceNum: list) -> int: # I really don't know what to say if you don't understand this part

    # fetch game phase score to determine game phase
    game_phase_score:int = get_game_phase_score(pceNum)

    # init game phase variable
    game_phase:int = -1

    # specify game phase var based on game phase score
    if game_phase_score > OPENING_PHASE_SCORE: game_phase = phases['opening']
    elif game_phase_score < ENDGAME_PHASE_SCORE: game_phase = phases['endgame']
    else: game_phase = phases['midgame']

    # define score variables
    score:int = 0; score_opening:int = 0; score_endgame:int = 0

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

    # determine the final score based on game phase
    # my nvim lsp keep throwing errors this things a nuisance, i need the exact float/value because better move ordering equals better playing strength
    if game_phase == phases['midgame']: score = float((score_opening * game_phase_score + score_endgame * (OPENING_PHASE_SCORE - game_phase_score)) / OPENING_PHASE_SCORE)
    elif game_phase == phases['opening']: score = float(score_opening)
    elif game_phase == phases['endgame']: score = float(score_endgame)

    # just debugging, no need to look at this
    game_phase_res:str = ''
    if not game_phase: game_phase_res = 'OPENING'
    elif game_phase == 1: game_phase_res = 'ENDGAME'
    elif game_phase == 2: game_phase_res = 'MIDDLEGAME'

    # print debug info
    print(f'  [GAME PHASE SCORE]: {game_phase_score}')
    print(f'  [GAME PHASE]: {game_phase_res}')
    print(f'  [STATIC EVAL, NO PERSPECTIVE]: {score}')

    # return the score, what else you expect
    # based on the side perspective of course
    return score if side else -score
