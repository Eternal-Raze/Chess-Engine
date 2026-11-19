import random
import shutil
import subprocess

piece_score = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "P": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2


'''
finds and makes a random, valid move
'''
def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves)-1)]


def _board_to_fen(gs):
    piece_map = {
        "wP": "P", "wN": "N", "wB": "B", "wR": "R", "wQ": "Q", "wK": "K",
        "bP": "p", "bN": "n", "bB": "b", "bR": "r", "bQ": "q", "bK": "k",
    }

    rows = []
    for row in gs.board:
        empty = 0
        fen_row = ""
        for square in row:
            if square == "--":
                empty += 1
            else:
                if empty:
                    fen_row += str(empty)
                    empty = 0
                fen_row += piece_map[square]
        if empty:
            fen_row += str(empty)
        rows.append(fen_row)

    board_part = "/".join(rows)
    turn_part = "w" if gs.white_to_move else "b"

    castling = ""
    if gs.current_castling_rights.wks:
        castling += "K"
    if gs.current_castling_rights.wqs:
        castling += "Q"
    if gs.current_castling_rights.bks:
        castling += "k"
    if gs.current_castling_rights.bqs:
        castling += "q"
    castling_part = castling if castling else "-"

    rows_to_ranks = {7: "1", 6: "2", 5: "3", 4: "4", 3: "5", 2: "6", 1: "7", 0: "8"}
    cols_to_files = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}

    if gs.en_passant_possible:
        r, c = gs.en_passant_possible
        en_passant_part = f"{cols_to_files[c]}{rows_to_ranks[r]}"
    else:
        en_passant_part = "-"

    halfmove_clock = 0
    fullmove_number = len(gs.move_log) // 2 + 1
    return f"{board_part} {turn_part} {castling_part} {en_passant_part} {halfmove_clock} {fullmove_number}"


def _move_to_uci(move):
    uci = move.get_chess_notation()
    if move.is_pawn_promotion:
        # Engine expects promotion piece, defaulting to queen in this project.
        uci += "q"
    return uci


def _square_to_row_col(square):
    """UCI square like 'e2' -> (row, col) in ChessEngine indexing (row 0 = rank 8)."""
    if len(square) != 2:
        return None
    col = ord(square[0]) - ord("a")
    rank = int(square[1])
    row = 8 - rank
    if not (0 <= row < 8 and 0 <= col < 8):
        return None
    return row, col


def _move_from_uci(valid_moves, uci):
    """
    Map engine UCI (e.g. e2e4, e7e8q) to our Move instance from valid_moves.
    Prefer exact string match, then fall back to coordinates (more reliable).
    """
    uci = uci.strip()
    if not uci or uci == "(none)":
        return None

    for move in valid_moves:
        if _move_to_uci(move) == uci:
            return move

    if len(uci) < 4:
        return None
    start_sq, end_sq = uci[0:2], uci[2:4]
    start = _square_to_row_col(start_sq)
    end = _square_to_row_col(end_sq)
    if start is None or end is None:
        return None
    sr, sc = start
    er, ec = end

    for move in valid_moves:
        if move.start_row == sr and move.start_col == sc and move.end_row == er and move.end_col == ec:
            return move
    return None


def _stockfish_candidates(preferred_path):
    seen = set()
    out = []
    for p in (
        preferred_path,
        shutil.which("stockfish"),
        "/opt/homebrew/bin/stockfish",
        "/usr/local/bin/stockfish",
    ):
        if p and p not in seen:
            seen.add(p)
            out.append(p)
    return out


def find_stockfish_move(gs, valid_moves, stockfish_path="stockfish", depth=18):
    """
    Ask Stockfish for a move and map it to this engine's Move object.
    Returns None on any failure so caller can gracefully fallback.
    """
    if not valid_moves:
        return None

    fen = _board_to_fen(gs)
    last_err = None

    for path in _stockfish_candidates(stockfish_path):
        process = None
        try:
            process = subprocess.Popen(
                [path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            def send(cmd):
                process.stdin.write(cmd + "\n")
                process.stdin.flush()

            send("uci")
            while True:
                line = process.stdout.readline()
                if not line:
                    raise OSError("Stockfish closed before uciok")
                if "uciok" in line:
                    break

            send("isready")
            while True:
                line = process.stdout.readline()
                if not line:
                    raise OSError("Stockfish closed before readyok")
                if "readyok" in line:
                    break

            send(f"position fen {fen}")
            send(f"go depth {depth}")

            bestmove_uci = None
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                line = line.strip()
                if line.startswith("bestmove"):
                    parts = line.split()
                    if len(parts) >= 2:
                        bestmove_uci = parts[1]
                    break

            move = _move_from_uci(valid_moves, bestmove_uci) if bestmove_uci else None
            if move is not None:
                return move
            last_err = f"bad reply or no matching move (uci={bestmove_uci!r})"
        except (FileNotFoundError, OSError, ValueError) as e:
            last_err = str(e)
            continue
        finally:
            if process is not None:
                try:
                    process.stdin.write("quit\n")
                    process.stdin.flush()
                except Exception:
                    pass
                process.terminate()

    if not getattr(find_stockfish_move, "_warned", False):
        find_stockfish_move._warned = True
        print(f"Stockfish unavailable ({last_err}); using built-in AI (depth {DEPTH}).")
    return None



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