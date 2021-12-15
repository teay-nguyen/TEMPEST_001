

import pygame as pyg
from highlighting import highlightSq

pyg.init()

DIMENSION = 8
WIDTH = HEIGHT = 512
SIZE = HEIGHT//DIMENSION

WHITE = pyg.Color('white')
GREY = pyg.Color('grey')


def DrawState(screen, board, loaded_pieces, validMoves, sqSelected, gs, size):
    DrawBoard(screen)
    highlightSq(screen, gs, validMoves, sqSelected, size)
    DrawPiece(screen, board, loaded_pieces)


def DrawBoard(screen):
    global colors
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


def animatemove(move, screen, board, clock, size, loaded_pieces):
    global colors

    dR = move.endRow-move.startRow
    dC = move.endCol-move.startCol

    fps = 5
    frameCount = (abs(dR)+abs(dC))*fps

    for frame in range(frameCount+1):
        r, c = (move.startRow+dR*frame/frameCount,
                move.startCol+dC*frame/frameCount)

        DrawBoard(screen)
        DrawPiece(screen, board, loaded_pieces)

        color = colors[(move.endRow+move.endCol) % 2]
        endSquare = pyg.Rect(move.endCol*size, move.endRow*size, size, size)
        pyg.draw.rect(screen, color, endSquare)

        if move.pieceCaptured != '--':
            screen.blit(loaded_pieces[move.pieceCaptured], endSquare)

        screen.blit(loaded_pieces[move.pieceMoved],
                    pyg.Rect(c*size, r*size, size, size))
        pyg.display.flip()
        clock.tick(60)
