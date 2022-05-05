#!/usr/bin/env pypy3 -u
# -*- coding: utf-8 -*-

# imports
from defs import *
from data import *
from copy import deepcopy
from eval import evaluate
from board0x88 import MovesStruct
from transposition import NO_HASH_ENTRY, HASH_ALPHA, HASH_BETA, HASH_EXACT, Transposition

# setup and define variables
killer_moves:list =                  [[0 for _ in range(MAX_PLY)] for _ in range(IDS)]
history_moves:list =    [[0 for _ in range(BOARD_SQ_NUM)] for _ in range(PIECE_TYPES)]
pv_table:list =                  [[0 for _ in range(MAX_PLY)] for _ in range(MAX_PLY)]
pv_length:list =                                           [0 for _ in range(MAX_PLY)]
ply:int =                                                                            0

# initialize the table
tt:Transposition = Transposition()
tt.tt_setsize(0x100000)

# "guess" the moves value and order them high up on the list if is a capture or is a killer move, if a move in the pv table is found, immediately return it as the best move
# for the engine to search

def score_move(board:list, move:int):
    # if a move is found in the pv table then order it up top in the list
    if pv_table[0][ply] == move: return 20000

    # get baseline score from mvv lva: "Most Valuable Victim" "Least Valuable Attacker/Aggressor"
    score:int = MVV_LVA[board[get_move_source(move)]][board[get_move_target(move)]]

    # if its a capture, search that move first
    if get_move_capture(move): score += 10000
    else:
        if killer_moves[0][ply] == move: return 9000
        elif killer_moves[1][ply] == move: return 8000
        else: return history_moves[board[get_move_source(move)]][get_move_target(move)] + 7000

    # return the score
    return score

# with the moves scored, we can then sort the moves based on the value, this is quite convenient as a built in "struct" with a score attribute is already present
# bubble sort would be the way to go because of its simplicity and easiness to write

def sort_moves(board:list, move_list):
    # loop through the move list and score the move, see "score_move"
    for count in range(move_list.count): move_list.moves[count].score = score_move(board, move_list.moves[count].move)

    # bubble sort the move list
    #for current in range(move_list.count):
    #    for next in range(current+1, move_list.count):
    #        if move_list.moves[current].score < move_list.moves[next].score:
    #            move_list.moves[current], move_list.moves[next] = move_list.moves[next], move_list.moves[current]

    move_list.moves.sort(reverse = True, key = lambda i: i.score)

# called when depth has reached 0, to check for any lingering captures left
def quiescence(alpha, beta, depth, state, nodes):
    # increment nodes and make ply variable global
    global ply

    nodes += 1

    # search went too deep
    if ply > MAX_PLY - 1: return evaluate(state.board, state.side, state.pce_count, state.hash_key)

    # stand pat for the function
    score:int = evaluate(state.board, state.side, state.pce_count, state.hash_key)

    # if higher or equal to beta then return beta, alpha acts as the max score so update it if needed
    # this is what people call a fail-hard beta cutoff
    if score >= beta: return beta
    alpha = max(alpha, score)

    # initalize move list, generate and sort moves
    move_list = MovesStruct()

    state.gen_moves(move_list)
    sort_moves(state.board, move_list)

    # loop through the move list
    for count in range(move_list.count):
        # copy the board state
        board_cpy:list = deepcopy(state.board)
        side_cpy:int = state.side
        xside_cpy:int = state.xside
        enpassant_cpy:int = state.enpassant
        castle_cpy:int = state.castle
        king_square_cpy:list = deepcopy(state.king_square)
        pce_count_cpy:list = deepcopy(state.pce_count)
        hashkey_cpy:int = state.hash_key

        # increment ply
        ply += 1

        # if is not a capture or legal move then decrement ply and move on to the next move
        if not state.make_move(move_list.moves[count].move, CAPTURE_MOVES):
            ply -= 1
            continue

        # recursive call
        score = -quiescence(-beta, -alpha, depth, state, nodes)

        # decrement ply
        ply -= 1

        # restore previous board state
        state.board = deepcopy(board_cpy)
        state.side = side_cpy
        state.xside = xside_cpy
        state.enpassant = enpassant_cpy
        state.castle = castle_cpy
        state.king_square = deepcopy(king_square_cpy)
        state.pce_count = deepcopy(pce_count_cpy)
        state.hash_key = hashkey_cpy

        # same as above
        if score > alpha:
            alpha = score
            if score >= beta:
                return beta

    # node position fails low
    return alpha

def search(alpha, beta, depth, state, nodes):
    # make ply global and update pv length
    global ply

    # init legal moves counter
    legal:int = 0

    # initialize pv length
    pv_length[ply] = ply

    # define hash flag
    hash_flag_:int = HASH_ALPHA

    # a small hack by Pedro Castro to figure out whether the current node is PV node or not
    pv_node = beta - alpha > 1

    # probe the hash table for any values
    score = tt.tt_probe(depth, alpha, beta, state.hash_key)
    if ply and score != NO_HASH_ENTRY and not pv_node: return score

    # if depth is 0 then activate quiescence search
    if not depth: return quiescence(alpha, beta, depth, state, nodes)

    # search went too high
    if ply > MAX_PLY - 1: return evaluate(state.board, state.side, state.pce_count, state.hash_key)

    # increment node count
    nodes += 1

    # if the king is incheck, then increase depth by 1
    in_check = state.is_square_attacked(state.king_square[state.side], state.xside)
    if in_check: depth += 1

    # initialize move list, generate and sort moves
    move_list = MovesStruct()

    state.gen_moves(move_list)
    sort_moves(state.board, move_list)

    moves_searched:int = 0

    # loop through the move list
    for count in range(move_list.count):
        board_cpy:list = deepcopy(state.board)
        side_cpy:int = state.side
        xside_cpy:int = state.xside
        enpassant_cpy:int = state.enpassant
        castle_cpy:int = state.castle
        king_square_cpy:list = deepcopy(state.king_square)
        pce_count_cpy:list = deepcopy(state.pce_count)
        hashkey_cpy:int = state.hash_key

        ply += 1

        if not state.make_move(move_list.moves[count].move, ALL_MOVES):
            ply -= 1
            continue

        legal += 1

        if not moves_searched: score = -search(-beta, -alpha, depth - 1, state, nodes)
        else:
            score = alpha + 1
            if score > alpha:
                score = -search(-alpha - 1, -alpha, depth - 1, state, nodes)
                if score > alpha and score < beta:
                    score = -search(-beta, -alpha, depth - 1, state, nodes)

        ply -= 1

        state.board = deepcopy(board_cpy)
        state.side = side_cpy
        state.xside = xside_cpy
        state.enpassant = enpassant_cpy
        state.castle = castle_cpy
        state.king_square = deepcopy(king_square_cpy)
        state.pce_count = deepcopy(pce_count_cpy)
        state.hash_key = hashkey_cpy

        moves_searched += 1

        if score > alpha:
            hash_flag_ = HASH_EXACT
            if not get_move_capture(move_list.moves[count].move): history_moves[state.board[get_move_source(move_list.moves[count].move)]][get_move_target(move_list.moves[count].move)] += depth
            alpha = score
            pv_table[ply][ply] = move_list.moves[count].move
            for next_ply in range(ply+1, pv_length[ply+1]): pv_table[ply][next_ply] = pv_table[ply+1][next_ply]
            pv_length[ply] = pv_length[ply+1]
            if score >= beta:
                tt.tt_save(depth, beta, HASH_BETA, state.hash_key)
                if not get_move_capture(move_list.moves[count].move):
                    killer_moves[1][ply] = killer_moves[0][ply]
                    killer_moves[0][ply] = move_list.moves[count].move
                return beta

    if not legal:
        if in_check: return -MATE_VALUE + ply
        else: return 0

    tt.tt_save(depth, alpha, hash_flag_, state.hash_key)

    return alpha
