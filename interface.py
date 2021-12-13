
import pygame as pyg
import os
from engine import State, Move

pyg.init()

DIMENSION = 8
WIDTH = HEIGHT = 512
SIZE = HEIGHT//DIMENSION
MAX_FPS = 15

BLACK = pyg.Color('black')
WHITE = pyg.Color('white')
GREY = pyg.Color('grey')


class Interface:
    def __init__(self):
        pass

    def get_pieces(self):
        PIECES = {}
        for fn in os.listdir('pieces'):
            full_path = os.path.join('pieces', fn)
            name = fn.replace('.png', '')
            PIECES[name] = pyg.transform.scale(
                pyg.image.load(full_path), (SIZE, SIZE))

        return PIECES

    def app_main_exec(self):
        screen = pyg.display.set_mode((WIDTH, HEIGHT))
        clock = pyg.time.Clock()
        state = State()
        pieces = self.get_pieces()
        running = True
        sq_selected = ()
        plr_clicks = []
        valid_moves = state.FilterValidMoves()
        moveMade = False

        screen.fill(WHITE)

        while running:
            for e in pyg.event.get():
                if e.type == pyg.QUIT:
                    running = False
                elif e.type == pyg.MOUSEBUTTONDOWN:
                    location = pyg.mouse.get_pos()
                    col = location[0]//SIZE
                    row = location[1]//SIZE
                    if sq_selected == (row, col):
                        sq_selected = ()
                        plr_clicks = []
                    else:
                        sq_selected = (row, col)
                        plr_clicks.append(sq_selected)

                    if len(plr_clicks) == 2:
                        move = Move(plr_clicks[0], plr_clicks[1], state.board)
                        print(move.getChessNotation())
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                state.make_move(valid_moves[i])
                                moveMade = True

                                sq_selected = ()
                                plr_clicks = []
                        if not moveMade:
                            plr_clicks = [sq_selected]

                elif e.type == pyg.KEYDOWN:
                    if e.key == pyg.K_z:
                        state.undo_move()
                        moveMade = True

            if moveMade:
                valid_moves = state.FilterValidMoves()
                moveMade = False

            self.draw_state(screen, state.board, pieces)
            clock.tick(MAX_FPS)
            pyg.display.flip()

    def draw_state(self, screen, board, loaded_pieces):
        self.draw_board(screen)
        self.draw_pieces(screen, board, loaded_pieces)

    def draw_board(self, screen):
        colors = [WHITE, GREY]
        for r in range(DIMENSION):
            for c in range(DIMENSION):
                color = colors[((r+c) % 2)]
                pyg.draw.rect(screen, color, pyg.Rect(
                    c*SIZE, r*SIZE, SIZE, SIZE))

    def draw_pieces(self, screen, board, loaded_pieces):
        for r in range(DIMENSION):
            for c in range(DIMENSION):
                piece = board[r, c]
                if piece != '--':
                    screen.blit(loaded_pieces[piece], pyg.Rect(
                        c*SIZE, r*SIZE, SIZE, SIZE))
