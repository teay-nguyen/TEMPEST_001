
from defs import *
from data import *
from copy import deepcopy
from eval import evaluate
from board0x88 import MovesStruct

killer_moves =                  [[0 for _ in range(MAX_PLY)] for _ in range(IDS)]
history_moves =    [[0 for _ in range(BOARD_SQ_NUM)] for _ in range(PIECE_TYPES)]
pv_table =                  [[0 for _ in range(MAX_PLY)] for _ in range(MAX_PLY)]
pv_length =                                           [0 for _ in range(MAX_PLY)]
ply = 0

def score_move(board:list, move:int):
    if pv_table[0][ply] == move:
        return 20000

    score:int = MVV_LVA[board[get_move_source(move)]][board[get_move_target(move)]]

    if get_move_capture(move): score += 10000
    else:
        if killer_moves[0][ply] == move: score = 9000
        elif killer_moves[1][ply] == move: score = 8000
        else: score = history_moves[board[get_move_source(move)]][get_move_target(move)] + 7000

    return score

def sort_moves(board:list, move_list):
    for count in range(move_list.count):
        move_list.moves[count].score = score_move(board, move_list.moves[count].move)

    for current in range(move_list.count):
        for next in range(current+1, move_list.count):
            if move_list.moves[current].score < move_list.moves[next].score:
                move_list.moves[current], move_list.moves[next] = move_list.moves[next], move_list.moves[current]

def quiesce_search(alpha, beta, depth, state, nodes):
    global ply
    nodes += 1

    score:int = evaluate(state.board, state.side, state.pce_count, state.hash_key)

    if score >= beta:
        return beta
    alpha = max(alpha, score)

    move_list = MovesStruct()

    state.gen_moves(move_list)
    sort_moves(state.board, move_list)

    for count in range(move_list.count):
        board_cpy:list = deepcopy(state.board)
        side_cpy:int = state.side
        xside_cpy:int = state.xside
        enpassant_cpy:int = state.enpassant
        castle_cpy:int = state.castle
        king_square_cpy:list = deepcopy(state.king_square)
        hashkey_cpy:int = state.hash_key

        ply += 1

        if not state.make_move(move_list.moves[count].move, CAPTURE_MOVES):
            ply -= 1
            continue

        eval = -quiesce_search(-beta, -alpha, depth, state, nodes)

        state.board = deepcopy(board_cpy)
        state.side = side_cpy
        state.xside = xside_cpy
        state.enpassant = enpassant_cpy
        state.castle = deepcopy(castle_cpy)
        state.king_square = deepcopy(king_square_cpy)
        state.hash_key = hashkey_cpy

        ply -= 1

        if eval >= beta:
            return beta
        alpha = max(eval, alpha)

    return alpha
