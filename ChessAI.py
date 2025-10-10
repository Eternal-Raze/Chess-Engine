import random

piece_score = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "P": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2


'''
finds and makes a random, valid move
'''
def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves)-1)]

'''
Finds best move, min max without recursion
'''
def find_best_move_minmax_no_recursion(gs, valid_moves):
    turn_multiplier = 1 if gs.white_to_move else -1
    opp_minmax_score = CHECKMATE
    best_player_move = None
    random.shuffle(valid_moves)
    for player_move in valid_moves:
        gs.make_move(player_move)
        opp_moves = gs.get_valid_moves()
        if gs.stalemate:
            opp_max_score = STALEMATE
        elif gs.checkmate:
            opp_max_score = -CHECKMATE
        else:
            opp_max_score = -CHECKMATE
            for opp_move in opp_moves:
                gs.make_move(opp_move)
                gs.get_valid_moves()
                if gs.checkmate:
                    score = -turn_multiplier * CHECKMATE
                elif gs.stalemate:
                    score = STALEMATE
                else:
                    score = -turn_multiplier * score_material(gs.board)
                if score > opp_max_score:
                    opp_max_score = score
                gs.undo_move()
        if opp_max_score < opp_minmax_score:
            opp_minmax_score = opp_max_score
            best_player_move = player_move
        gs.undo_move()
    print(score)
    return best_player_move

'''
Helper method to make first recursive call
'''
def find_best_move(gs, valid_moves):
    global next_move, counter
    next_move = None
    counter = 0
    random.shuffle(valid_moves)
    #find_move_minmax(gs, valid_moves, DEPTH, gs.white_to_move)
    #find_move_nega_max(gs, valid_moves, DEPTH, 1 if gs.white_to_move else -1)
    find_move_nega_max_alpha_beta(gs, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.white_to_move else -1)
    print(counter)
    return next_move

def find_move_nega_max_alpha_beta(gs, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_move, counter
    counter += 1
    if depth == 0:
        return turn_multiplier * score_board(gs)
    
    #move ordering
    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -find_move_nega_max_alpha_beta(gs, next_moves, depth-1,-beta, -alpha, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()
        if max_score > alpha: #pruning happens
            alpha = max_score
        if alpha >= beta:
            break
    return max_score
    
'''
Positive score is good for white, negative score is good for black
'''
def score_board(gs):
    if gs.checkmate:
        if gs.white_to_move:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE
    
    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == "w":
                score += piece_score[square[1]]
            elif square[0] == "b":
                score -= piece_score[square[1]]
    return score

'''
Score board based on material
'''
def score_material(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += piece_score[square[1]]
            elif square[0] == "b":
                score -= piece_score[square[1]]
    return score