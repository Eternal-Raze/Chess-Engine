import pygame as p
import ChessMain, LoginSystem

p.init()

WIDTH = 500
HEIGHT = 500

screen = p.display.set_mode((WIDTH, HEIGHT))

p.display.set_caption("Menu")
fps = 60
timer = p.time.Clock()
main_menu = True
font = p.font.Font('freesansbold.ttf', 24)
menu_command = 0
run = True

class Button:
    def __init__(self, txt, pos):
        self.text = txt
        self.pos = pos
        self.button = p.rect.Rect((self.pos[0], self.pos[1]), (260, 40))
        
    def draw(self):
        button = p.draw.rect(screen, "#8c5630", self.button, 0, 5)
        p.draw.rect(screen, "Black", self.button, 2, 5)
        text = font.render(self.text, True, 'black')
        screen.blit(text, (self.pos[0] + 15, self.pos[1] + 7))
    
    def check_clicked(self):
        if self.button.collidepoint(p.mouse.get_pos()) and p.mouse.get_pressed()[0]:
            return True
        else:
            return False

def draw_game():
    button = Button('Main Menu', (230, 450))
    button.draw()
    return button.check_clicked()

def draw_menu():
    command = 0
    p.draw.rect(screen, '#333333', [100, 100, 300, 300])
    #exit menu button
    menu_button = Button('Exit Menu', (120, 350))
    singleplayer_btn = Button('Single Player', (120, 250))
    twoplayer_btn = Button('2 Player', (120, 300))
    tutorial_btn = Button("Tutorial", (120, 200))
    menu_button.draw()
    singleplayer_btn.draw()
    twoplayer_btn.draw()
    tutorial_btn.draw()
    if menu_button.check_clicked():
        command = 1
    if singleplayer_btn.check_clicked():
        command = 2
    if twoplayer_btn.check_clicked():
        command = 3
    if tutorial_btn.check_clicked():
        command = 4
        
    return command

while run:
    screen.fill("#333333")
    timer.tick(fps)
    if main_menu:
        menu_command = draw_menu()
        if menu_command > 0:
            main_menu = False
    else:
        main_menu = draw_game()
        if menu_command == 4:
            LoginSystem.help_tool()
    
    for event in p.event.get():
        if event.type == p.QUIT:
            run = False
            
    p.display.flip()

p.quit()
