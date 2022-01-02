
import pygame as pyg
import os
from engine import State, Move
from draw_board import DrawState, animatemove
from DepthLiteThink import DepthLite1
from multiprocessing import Process, Queue

pyg.init()

WIDTH = HEIGHT = 800
PANEL_WIDTH = 250
PANEL_HEIGHT = HEIGHT
DIMENSION = 8
SIZE = HEIGHT//DIMENSION
MAX_FPS = 15

WHITE = pyg.Color('white')
GREY = pyg.Color('grey')


class human_plr:
    def __init__(self, plr1, plr2):
        self.plr1 = plr1
        self.plr2 = plr2


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
        DepthLite = DepthLite1()
        screen = pyg.display.set_mode((WIDTH+PANEL_WIDTH, HEIGHT))
        clock = pyg.time.Clock()
        state = State()
        pieces = self.get_pieces()
        running = True
        animate = False
        sq_selected = ()
        plr_clicks = []
        valid_moves = state.FilterValidMoves()
        moveMade = False

        screen.fill(WHITE)

        plrChoice1 = None
        plrChoice2 = None
        AIThinking = False
        movefinderprocess = None

        Options = [
            'True',
            'False',
        ]

        while not plrChoice1 in Options:
            try:
                plrChoice1 = input('1. HUMAN OR AI: True or False --> ')
            except Exception:
                print('NOT A VALID INPUT')

        while not plrChoice2 in Options:
            try:
                plrChoice2 = input('2. HUMAN OR AI: True or False --> ')
            except Exception:
                print('NOT A VALID INPUT')

        plr1 = eval(plrChoice1)
        plr2 = eval(plrChoice2)

        humanPlr = human_plr(plr1, plr2)

        while running:
            human_turn = (state.whitesturn and humanPlr.plr1) or (
                not state.whitesturn and humanPlr.plr2)

            for e in pyg.event.get():
                if e.type == pyg.QUIT:
                    running = False
                elif e.type == pyg.MOUSEBUTTONDOWN:
                    if human_turn:
                        location = pyg.mouse.get_pos()
                        col = location[0]//SIZE
                        row = location[1]//SIZE
                        if not col > 7:
                            if sq_selected == (row, col):
                                sq_selected = ()
                                plr_clicks = []
                            else:
                                sq_selected = (row, col)
                                plr_clicks.append(sq_selected)

                            if len(plr_clicks) == 2:
                                move = Move(plr_clicks[0],
                                            plr_clicks[1], state.board)
                                for i in range(len(valid_moves)):
                                    if move == valid_moves[i]:
                                        state.make_move(valid_moves[i])
                                        moveMade = True
                                        animate = True

                                        sq_selected = ()
                                        plr_clicks = []

                                if not moveMade:
                                    plr_clicks = [sq_selected]

                elif e.type == pyg.KEYDOWN:
                    if e.key == pyg.K_z:
                        state.undo_move()
                        moveMade = True
                    if e.key == pyg.K_r:
                        state = State()
                        valid_moves = state.FilterValidMoves()
                        sq_selected = ()
                        plr_clicks = []
                        moveMade = False
                        animate = False
                    if e.key == pyg.K_q:
                        running = False

            if not human_turn:
                if not AIThinking:
                    AIThinking = True
                    print('THINKING...')

                    AIMove = DepthLite.startSearch(state)
                    if AIMove is None:
                        AIMove = DepthLite.random_move(state)
                    elif AIMove == 1:
                        running = False

                    state.make_move(AIMove)
                    moveMade = True
                    animate = True
                    AIThinking = False
                    print('DONE THINKING')

            if moveMade:
                if animate:
                    animatemove(state.moveLog[-1], screen,
                                state.board, clock, SIZE, pieces)
                valid_moves = state.FilterValidMoves()
                moveMade = False
                animate = False

            DrawState(screen, state.board, pieces,
                      valid_moves, sq_selected, state, SIZE)
            clock.tick(MAX_FPS)
            pyg.display.flip()

    '''
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
    '''
