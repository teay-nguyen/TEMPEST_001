
import pygame as pyg
from engine import State, Move
from draw_board import DrawState, animatemove
from search import searcher
from piece import get_pieces

pyg.init()

class human_plr:
    def __init__(self, plr1, plr2):
        self.plr1 = plr1
        self.plr2 = plr2

class uni_pieces:
    def __init__(self):
        self.uni_pieces = {
            'wK':'K',
            'wQ':'Q',
            'wR':'R',
            'wB':'B',
            'wN':'N',
            'wp':'P',
            'bK':'k',
            'bQ':'q',
            'bR':'r',
            'bB':'b',
            'bN':'n',
            'bp':'p',
            '--':"'",
        }

class Interface:
    def __init__(self):
        self.WIDTH = self.HEIGHT = 800
        self.PANEL_WIDTH = 250
        self.PANEL_HEIGHT = self.HEIGHT
        self.DIMENSION = 8
        self.SIZE = self.HEIGHT//self.DIMENSION
        self.MAX_FPS = 30

        self.WHITE = pyg.Color('white')
        self.GREY = pyg.Color('grey')
        self.animateMove = False

        self.unipieces = uni_pieces()

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

    def render(self, state: State):
        rendered_string = '\n'
        for row in range(len(state.board)):
            for col in range(len(state.board[row])):
                char = state.board[row][col]
                if char in self.unipieces.uni_pieces:
                    rendered_string += self.unipieces.uni_pieces[char] + ' '
            rendered_string += '\n'
        return rendered_string

    def app_main_exec(self):
        _searcher = searcher()
        screen = pyg.display.set_mode((self.WIDTH + self.PANEL_WIDTH, self.HEIGHT))
        clock = pyg.time.Clock()
        state = State()
        pieces = self.get_pieces()
        running = 1
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
                    running = 0
                elif e.type == pyg.MOUSEBUTTONDOWN:
                    if human_turn:
                        location = pyg.mouse.get_pos()
                        col = location[0] // self.SIZE
                        row = location[1] // self.SIZE
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
                                        if self.animateMove: animate = True

                                        sq_selected = ()
                                        plr_clicks = []

                                        print(self.render(state))

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
                        running = 0

            if not human_turn:
                if not AIThinking:
                    AIThinking = True
                    AIMove = _searcher.startSearch(state)
                    if AIMove is None:
                        AIMove = _searcher.random_move(state)
                    elif AIMove == 1:
                        running = 0
                        quit()

                    state.make_move(AIMove)
                    moveMade = True
                    if self.animateMove: animate = True
                    AIThinking = False
                    print(self.render(state))

            if moveMade:
                if animate:
                    animatemove(state.moveLog[-1], screen, state.board, clock, self.SIZE, pieces)
                valid_moves = state.FilterValidMoves()
                moveMade = False
                animate = False

            DrawState(screen, state.board, pieces,
                      valid_moves, sq_selected, state, self.SIZE)
            
            clock.tick(self.MAX_FPS)
            pyg.display.flip()
