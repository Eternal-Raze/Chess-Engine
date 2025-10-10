"""
this python file its for recording the state that the game is in,creating a class for this.
it will also determine valid moves and record the moves being made
"""
class GameState():
    def __init__(self):
        #creating a 2D list for the 8x8 boad with 2 characters each. 
        # the first is the colour of the piece and the other is the character name and the -- = blank square
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.move_function = {"P": self.get_pawn_moves, "R": self.get_rook_moves, "N": self.get_knight_moves,
                              "B": self.get_bishop_moves, "Q": self.get_queen_moves, "K": self.get_king_moves}

        self.white_to_move = True
        self.move_log = [] #records the moves being made
        self.white_king_location = (7,4)
        self.black_king_location = (0,4)
        self.checkmate = False
        self.stalemate = False
        self.en_passant_possible = () #cooridnates of the square where en passant is possible
        self.current_castling_rights = CastleRights(True, True, True, True)
        #keeps track of the castle rights during the game
        self.castle_rights_log = [CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                               self.current_castling_rights.wqs, self.current_castling_rights.bqs)]


    '''
    Takes a move as a parameter and executes it on the board
    '''
    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move) #log the move so we can undo it later
        self.white_to_move = not self.white_to_move #switch players
        #update king location if moved
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_col)
        if move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_col)
        #Pawn promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + "Q"
        #en passant move
        if move.is_en_passant_move:
            self.board[move.start_row][move.end_col] = "--"  # capturing pawn
        #update en_passant_possible variable
        if move.piece_moved[1] == "P" and abs(move.start_row - move.end_row) == 2: #only on 2 square pawn advances
            self.en_passant_possible = ((move.start_row + move.end_row)//2, move.start_col)
        else:
            self.en_passant_possible = ()
            
        #castle move
        if move.is_castle_move:
            if move.end_col - move.start_col == 2: #kingside castle
                self.board[move.end_row][move.end_col-1] = self.board[move.end_row][move.end_col+1] #moves rook
                self.board[move.end_row][move.end_col+1] = "--" #delete old rook
            else: #queenside castle
                self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-2]
                self.board[move.end_row][move.end_col-2] = "--" 

        #update castling rights
        self.update_castle_rights(move)
        self.castle_rights_log.append(CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                                   self.current_castling_rights.wqs, self.current_castling_rights.bqs))



    """
    undo the last move
    """
    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move #switch turn back
            #update king position of needed
            if move.piece_moved == "wK":
                self.white_king_location = (move.start_row, move.start_col)
            if move.piece_moved == "bK":
                self.black_king_location = (move.start_row, move.start_col)
            #undo en passant move
            if move.is_en_passant_move:
                self.board[move.end_row][move.end_col] = "--" #leave landing square blank
                self.board[move.start_row][move.end_col] = move.piece_captured
                self.en_passant_possible = (move.end_row, move.end_col)
            #undo 2 square pawn advance
            if move.piece_moved[1] == "P" and abs(move.start_row - move.end_row) == 2:
                self.en_passant_possible = ()
            #undo castling rights
            self.castle_rights_log.pop() #delete castle rignts from move we are undoing
            new_rights = self.castle_rights_log[-1]
            #set current castling rights to the last one in the list
            self.current_castling_rights = CastleRights(new_rights.wks, new_rights.bks, new_rights.wqs, new_rights.bqs)
            #undo castle moves
            if move.is_castle_move:
                if move.end_col - move.start_col == 2: #kingside castle
                    self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-1] #moves rook
                    self.board[move.end_row][move.end_col-1] = "--" #delete old rook
                else: #queenside castle
                    self.board[move.end_row][move.end_col-2] = self.board[move.end_row][move.end_col+1]
                    self.board[move.end_row][move.end_col+1] = "--"
            
            self.checkmate = False
            self.stalemate = False


    '''
    update castle rights given the move
    '''
    def update_castle_rights(self, move):
        if move.piece_moved == "wK":
            self.current_castling_rights.wks = False
            self.current_castling_rights.wqs = False
        elif move.piece_moved == "bK":
            self.current_castling_rights.bks = False
            self.current_castling_rights.bqs = False
        elif move.piece_moved == "wR":
            if move.start_row == 7:
                if move.start_col == 0: #left rook
                    self.current_castling_rights.wqs = False
                elif move.start_col == 7: #right rook
                    self.current_castling_rights.wks = False
        elif move.piece_moved == "bR":
            if move.start_row == 0:
                if move.start_col == 0: #left rook
                    self.current_castling_rights.bqs = False
                elif move.start_col == 7: #right rook
                    self.current_castling_rights.bks = False

    '''
    gets all possible moves and removes any moves that aren't legal
    '''
    def get_valid_moves(self):
        temp_en_passant_possible = self.en_passant_possible
        temp_castle_rights = CastleRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                          self.current_castling_rights.wqs, self.current_castling_rights.bqs)
        moves = self.get_all_possible_moves()
        if self.white_to_move:
            self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)
        else:
            self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)
        for i in range(len(moves)-1, -1, -1):
            self.make_move(moves[i])
            self.white_to_move = not self.white_to_move
            if self.in_check():
                moves.remove(moves[i])
            self.white_to_move = not self.white_to_move
            self.undo_move()
        if len(moves) == 0: #either checkmate or stalemate
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True

        self.en_passant_possible = temp_en_passant_possible
        self.current_castling_rights = temp_castle_rights
        return moves

    """
    Determine if current player is in check
    """
    def in_check(self):
        if self.white_to_move:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])


    """
    Determine if the enemy can attack square r, c
    """
    def square_under_attack(self, r, c):
        self.white_to_move = not self.white_to_move # switch to opponent turn
        opp_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move
        for move in opp_moves:
            if move.end_row == r and move.end_col == c: # square is under attack
                return True
        return False

    '''
    Gets all the possible moves
    '''
    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == "w" and self.white_to_move) or (turn == "b" and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_function[piece](r, c, moves) #calls appropiate move function based on piece type
        return moves

    '''
    Rules for pawn moves
    '''
    def get_pawn_moves(self, r, c, moves):
        if self.white_to_move:
            if self.board[r-1][c] == "--": # 1 square move
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--": # 2 square moves
                    moves.append(Move((r, c), (r-2, c), self.board))
            if c-1 >= 0: #captures to the left
                if self.board[r-1][c-1][0] == "b": #enemy piece
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.en_passant_possible:
                    moves.append(Move((r, c), (r-1, c-1), self.board, is_en_passant_move=True))
            if c+1 <= 7: #captures to the right
                if self.board[r-1][c+1][0] == "b":
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.en_passant_possible:
                    moves.append(Move((r, c), (r-1, c+1), self.board, is_en_passant_move=True))

        else: #black pawn moves
            if self.board[r+1][c] == "--": # 1 square move
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--": # 2 square moves
                    moves.append(Move((r, c), (r+2, c), self.board))
            # captures
            if c-1 >= 0: #captures to the left
                if self.board[r+1][c-1][0] == "w":
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.en_passant_possible:
                    moves.append(Move((r, c), (r+1, c-1), self.board, is_en_passant_move=True))
            if c+1 <= 7: #captures to the right
                if self.board[r+1][c+1][0] == "w":
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.en_passant_possible:
                    moves.append(Move((r, c), (r+1, c+1), self.board, is_en_passant_move=True))

    '''
    Rules for rook moves
    '''
    def get_rook_moves(self, r, c, moves):
        directions = ((-1,0), (0,-1), (1,0), (0,1)) #up, left, down, right
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1,8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    '''
    Rules for knight moves
    '''
    def get_knight_moves(self, r, c, moves):
        knight_moves = ((-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1))
        ally_color = "w" if self.white_to_move else "b"
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    '''
    Rules for bishop moves
    '''
    def get_bishop_moves(self, r, c, moves):
        directions = ((-1,-1), (-1,1), (1,-1), (1,1))
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1,8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    '''
    Rules for queen moves
    '''
    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    '''
    Rules for king moves
    '''
    def get_king_moves(self, r, c, moves):
        king_moves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        ally_color = "w" if self.white_to_move else "b"
        for i in range(8):
            end_row = r + king_moves[i][0]
            end_col = c + king_moves[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))
        
    '''
    Generate all valid castle moves for the king at (r, c) and add to list of moves
    '''
    def get_castle_moves(self, r, c, moves):
        if self.square_under_attack(r, c):
            return #cant castle while in check
        if (self.white_to_move and self.current_castling_rights.wks) or (not self.white_to_move and self.current_castling_rights.bks):
            self.get_kingside_castle_moves(r, c, moves)
        if (self.white_to_move and self.current_castling_rights.wqs) or (not self.white_to_move and self.current_castling_rights.bqs):
            self.get_queenside_castle_moves(r, c, moves)
        
    '''
    Determines if kingside castling is allowed
    '''
    def get_kingside_castle_moves(self, r, c, moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.square_under_attack(r, c+1) and not self.square_under_attack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, is_castle_move = True))
    
    '''
    Determines if queenside castling is allowed
    '''
    def get_queenside_castle_moves(self, r, c, moves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--":
            if not self.square_under_attack(r, c-1) and not self.square_under_attack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, is_castle_move = True))
    
'''
This class is for recording the boolean values of each type of castling
'''
class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


'''
This class is for recording the moves that are being made
'''
class Move():
    #maps keys to values
    #key: value
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, is_en_passant_move = False, is_castle_move = False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        #pawn promotion
        self.is_pawn_promotion = (self.piece_moved == "wP" and self.end_row == 0) or (self.piece_moved == "bP" and self.end_row == 7)
        #en passant
        self.is_en_passant_move = is_en_passant_move
        if self.is_en_passant_move:
            self.piece_captured = "wP" if self.piece_moved == "bP" else "bP"
        #castle move
        self.is_castle_move = is_castle_move

        self.moveID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
        #print(self.moveID)

    '''
    Overriding the equals method
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
      return self.cols_to_files[c] + self.rows_to_ranks[r]