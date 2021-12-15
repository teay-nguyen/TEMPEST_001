

import pygame as pyg

pyg.init()

DIMENSION = 8
WIDTH = HEIGHT = 512
SIZE = HEIGHT//DIMENSION

WHITE = pyg.Color('white')
GREY = pyg.Color('grey')


def DrawState(screen, board, loaded_pieces):
    DrawBoard(screen)
    DrawPiece(screen, board, loaded_pieces)


def DrawBoard(screen):
    colors = [WHITE, GREY]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            pyg.draw.rect(screen, color, pyg.Rect(c*SIZE, r*SIZE, SIZE, SIZE))


def DrawPiece(screen, board, loaded_pieces):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r, c]
            if piece != '--':
                screen.blit(loaded_pieces[piece], pyg.Rect(
                    c*SIZE, r*SIZE, SIZE, SIZE))
