
import pygame as pyg
from engine import State, Move
from draw_board import DrawState, animatemove
from DepthLiteThink import DepthLite1
from PieceTheme import get_pieces

pyg.init()

class human_plr:
    def __init__(self, plr1, plr2):
        self.plr1 = plr1
        self.plr2 = plr2


class Interface:
    def __init__(self):
        self.WIDTH = self.HEIGHT = 800
        self.PANEL_WIDTH = 250
        self.PANEL_HEIGHT = self.HEIGHT
        self.DIMENSION = 8
        self.SIZE = self.HEIGHT//self.DIMENSION
        self.MAX_FPS = 15

        self.WHITE = pyg.Color('white')
        self.GREY = pyg.Color('grey')

    def get_pieces(self):
        return get_pieces(self)
    
    def initialize(self):
        plrChoice1 = ''
        plrChoice2 = ''
        AIThinking = False

        Options = [
            'True',
            'False',
        ]

        while not plrChoice1.capitalize() in Options:
            try:
                plrChoice1 = input('1. HUMAN OR AI: True or False --> ').capitalize()
            except Exception:
                print('NOT A VALID INPUT')

        while not plrChoice2.capitalize() in Options:
            try:
                plrChoice2 = input('2. HUMAN OR AI: True or False --> ').capitalize()
            except Exception:
                print('NOT A VALID INPUT')

        plr1 = eval(plrChoice1)
        plr2 = eval(plrChoice2)

        return plr1, plr2, AIThinking

    def app_main_exec(self):
        DepthLite = DepthLite1()
        screen = pyg.display.set_mode((self.WIDTH + self.PANEL_WIDTH, self.HEIGHT))
        clock = pyg.time.Clock()
        state = State()
        pieces = self.get_pieces()
        running = True
        animate = False
        sq_selected = ()
        plr_clicks = []
        valid_moves = state.FilterValidMoves()
        moveMade = False

        screen.fill(self.WHITE)

        plr1, plr2, AIThinking = self.initialize()
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
                        col = location[0]//self.SIZE
                        row = location[1]//self.SIZE
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

                                if move in valid_moves:
                                    state.make_move(move)
                                    moveMade = True
                                    animate = True

                                    sq_selected = ()
                                    plr_clicks = []

                                '''
                                for i in range(len(valid_moves)):
                                    if move == valid_moves[i]:
                                        state.make_move(valid_moves[i])
                                        moveMade = True
                                        animate = True

                                        sq_selected = ()
                                        plr_clicks = []
                                '''

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
                                state.board, clock, self.SIZE, pieces)
                valid_moves = state.FilterValidMoves()
                moveMade = False
                animate = False

            DrawState(screen, state.board, pieces,
                      valid_moves, sq_selected, state, self.SIZE)
            
            clock.tick(self.MAX_FPS)
            pyg.display.flip()
