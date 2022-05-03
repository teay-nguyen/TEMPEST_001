
from data import *
from defs import *
from transposition import Transposition, NO_HASH_ENTRY

# initialize the transposition table
tt = Transposition()
tt.tteval_setsize(0x100000)

# predefined variables so code can be more readable
PAWN:int = 0; KNIGHT:int = 1; BISHOP:int = 2; ROOK:int = 3; QUEEN:int = 4; KING:int = 5

# other tools to help with eval
supported:list = [[-15, -17], [15, 17]]

def eval_pawn(board, sq, side) -> int:
    # check side
    if side:
        if board[sq] != P: return 0
    else:
        if board[sq] != p: return 0

    # define vars
    score:int = 0
    flagIsWeak:int = 1
    flagIsDoubled:int = 0

    # calc pawn score based on doubled pawns and supported pawns
    if side:
        if (board[sq + supported[1][0]] == P and 0 <= (sq + supported[1][0]) <= 127) or (board[sq + supported[1][1]] == P and 0 <= (sq + supported[1][1]) <= 127):
            flagIsWeak = 0
            score += SUPPORTED_BONUS
        else: score -= NOT_SUPPORTED_PENALTY
        if 0 <= (sq - 16) <= 127:
            if board[sq - 16] == P:
                flagIsDoubled = 1
                score -= DOUBLED_PENALTY
            else: score += NOT_DOUBLED_BONUS
    else:
        if (board[sq + supported[0][0]] == p and 0 <= (sq + supported[0][0]) <= 127) or (board[sq + supported[0][1]] == p and 0 <= (sq + supported[0][1]) <= 127):
            flagIsWeak = 0
            score += SUPPORTED_BONUS
        else: score -= NOT_SUPPORTED_PENALTY
        if 0 <= (sq + 16) <= 127:
            if board[sq + 16] == p:
                flagIsDoubled = 1
                score -= DOUBLED_PENALTY
            else: score += NOT_DOUBLED_BONUS

    # calculate the penalty based on doubled pawns and weak pawns
    penalty = 13 * (flagIsWeak + flagIsDoubled)

    # return the score deducting penalty
    return score - penalty

# score to determine the game phase
def get_game_phase_score(pceNum:list) -> int:
    # define the variables
    wp_scores:int = 0; bp_scores:int = 0

    # loop through pieces and add them to the variables
    for piece in range(N, K): wp_scores += pceNum[piece] * piece_val[phases['opening']][piece]
    for piece in range(n, k): bp_scores += pceNum[piece] * -piece_val[phases['opening']][piece]

    # return the total amount of material, minus the pawns
    return (wp_scores + bp_scores)

# main driver
def evaluate(board: list, side: int, pceNum: list, hashkey: int) -> int:

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
    score:int = 0; score_opening:int = 0; score_endgame:int = 0

    # pair bonuses
    if pceNum[B] > 1:
        score_opening += BISHOP_PAIR
        score_endgame += BISHOP_PAIR

    if pceNum[b] > 1:
        score_opening -= BISHOP_PAIR
        score_endgame -= BISHOP_PAIR

    if pceNum[N] > 1:
        score_opening += KNIGHT_PAIR
        score_endgame += KNIGHT_PAIR

    if pceNum[n] > 1:
        score_opening -= KNIGHT_PAIR
        score_endgame -= KNIGHT_PAIR

    if pceNum[R] > 1:
        score_opening += ROOK_PAIR
        score_endgame += ROOK_PAIR

    if pceNum[r] > 1:
        score_opening -= ROOK_PAIR
        score_endgame -= ROOK_PAIR

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
    if game_phase == phases['midgame']: score = float((score_opening * game_phase_score + score_endgame * (OPENING_PHASE_SCORE - game_phase_score)) / OPENING_PHASE_SCORE)
    elif game_phase == phases['opening']: score = float(score_opening)
    elif game_phase == phases['endgame']: score = float(score_endgame)

    # change the score based on stm, required on the negamax framework
    if side == sides['black']:
        score = -score

    # store the score in the tt table in case of encountering this position again
    tt.tteval_save(score, hashkey)

    # return the score
    return score
