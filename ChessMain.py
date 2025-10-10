'''
This is our main driver file, it will be responsible for handling user input and displaying the current GameState
'''
import pygame as p
import ChessEngine, ChessAI

WIDTH = HEIGHT = 512 #square board
DIMENSIONS = 8 #dimensions of squares on board
SQ_SIZE = WIDTH // DIMENSIONS
MAX_FPS = 15 #for animation
IMAGES = {}

"""
Initialising a global dictionary of chess piece images, going to be called only once 
"""

def load_images():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bP", "wR", "wN", "wB", "wQ", "wK", "wP"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/"+ piece + ".png"), (SQ_SIZE, SQ_SIZE))


def main():
    p.init() #initialising pygame
    screen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption("Chess")
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False #flag variable for when a move is made
    animate = True #flag variable for when we should animate a move
    load_images()
    running = True
    sq_selected = () #keep track of the last click of the user (tuple:(row, col))
    player_clicks = [] #keep track of player clicks (two tuples)
    game_over = False
    player1 = True #if human playing white, vaiable set to true. If AI playing white then false
    player2 = False #same as above but for black
    while running:
        human_turn = (gs.white_to_move and player1) or (not gs.white_to_move and player2)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos() #stores x,y value of mouse at given point
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sq_selected == (row, col): #user clicks the same sqare twice
                        sq_selected = () #deselect
                        player_clicks = [] #clear player clicks
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected) #append for both 1st and 2nd clicks
                    if len(player_clicks) == 2: #after 2nd click
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                        print(move.get_chess_notation())
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                sq_selected = () #reset user clicks
                                player_clicks = []
                        if not move_made:
                            player_clicks = [sq_selected]
            #key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when 'z' is pressed
                    gs.undo_move()
                    move_made = True
                    animate = False
                    game_over = False
                if e.key == p.K_r: #reset board when "r" is pressed
                    gs = ChessEngine.GameState()
                    valid_moves = gs.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False

        #AI move finder
        if not game_over and not human_turn:
            AI_move = ChessAI.find_best_move(gs, valid_moves)
            if AI_move is None:
                AI_move = ChessAI.find_random_move(valid_moves)
            gs.make_move(AI_move)
            move_made = True
            animate = True

        #animating last move made
        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False
            
        draw_GameState(screen, gs, valid_moves, sq_selected)
        
        if gs.checkmate:
            game_over = True
            if gs.white_to_move:
                draw_text(screen, 'Black wins by checkmate')
            else:
                draw_text(screen, 'White wins by checkmate')
        elif gs.stalemate:
            game_over = True
            draw_text(screen, "Stalemate")
                          
        clock.tick(MAX_FPS)
        p.display.flip()

'''
Highlight square selected and valid moves for piece selected 
'''
def highlight_squares(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ("w" if gs.white_to_move else "b"): #sq_selected is a piece that can be moved
            #highlights square selected
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) #sets transparency value
            s.fill(p.Color("blue"))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            #highlight moves from that square
            s.fill(p.Color("#edd328"))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col*SQ_SIZE, move.end_row*SQ_SIZE))
                    
                           
'''
Responsible for all the graphics within a current game state
'''
def draw_GameState(screen, gs, valid_moves, sq_selected):
    draw_board(screen) #draws squares on the board
    highlight_squares(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs.board) #draw pieces on top of board


'''
Displays the sqaures on the board
'''
def draw_board(screen):
    global colors
    colors = [p.Color("#C4A484"), p.Color("#8c5630")]
    for r in range(DIMENSIONS):
        for c in range(DIMENSIONS):
            colour = colors[((r+c) % 2)]
            p.draw.rect(screen, colour, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Draw the pieces on the board using the current GameState.board
'''
def draw_pieces(screen, board):
    for r in range(DIMENSIONS):
        for c in range(DIMENSIONS):
            piece = board[r][c]
            if piece != "--": #not empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

'''
Animating a move
'''
def animate_move(move, screen, board, clock):
    global colors
    dR = move.end_row - move.start_row
    dC = move.end_col - move.start_col
    frames_per_square = 2 #frames to move one square
    frame_count = (abs(dR) + abs(dC)) * frames_per_square
    for frame in range(frame_count+1):
        r, c = (move.start_row + dR*frame/frame_count, move.start_col + dC*frame/frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        #erase piece moved from its ending square
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col*SQ_SIZE, move.end_row*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        #draw captured piece onto rectangle
        if move.piece_captured != "--":
            screen.blit(IMAGES[move.piece_captured], end_square)
        #draw moving piece
        screen.blit(IMAGES[move.piece_moved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


'''
Draws end text when game is over
'''
def draw_text(screen, text):
    font = p.font.SysFont("Aharoni", 40, True, False)
    text_object = font.render(text, 0, p.Color("Gray"))
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - text_object.get_width()/2, HEIGHT/2 - text_object.get_height()/2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, 0, p.Color("Black"))
    screen.blit(text_object, text_location.move(2, 2))

if __name__ == "__main__":
    main()
