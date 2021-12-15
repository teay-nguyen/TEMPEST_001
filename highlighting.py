import pygame as pyg

pyg.init()

BLUE = pyg.Color('blue')
YELLOW = pyg.Color('yellow')


def highlightSq(screen, gs, validMoves, sq_selected, size):
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r, c][0] == ('w' if gs.whitesturn else 'b'):
            s = pyg.Surface((size, size))
            s.set_alpha(100)
            s.fill(BLUE)
            screen.blit(s, (c*size, r*size))
            s.fill(YELLOW)
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*size, move.endRow*size))
