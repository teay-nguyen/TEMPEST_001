import pygame as pyg
from highlighting import highlightSq

pyg.init()

WIDTH = HEIGHT = 800
PANEL_WIDTH = 250
PANEL_HEIGHT = HEIGHT
DIMENSION = 8
SIZE = HEIGHT // DIMENSION

WHITE = pyg.Color("white")
GREY = pyg.Color("grey")
BLACK = pyg.Color("black")

YELLOW = (253, 238, 211)
BROWN = (186, 148, 125)


def DrawState(screen, board, loaded_pieces, validMoves, sqSelected, gs, size):
    DrawBoard(screen)
    highlightSq(screen, gs, validMoves, sqSelected, size)
    DrawPiece(screen, board, loaded_pieces)
    drawMoveLog(screen, gs)


def DrawBoard(screen):
    global colors
    colors = [YELLOW, BROWN]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            pyg.draw.rect(screen, color, pyg.Rect(c * SIZE, r * SIZE, SIZE, SIZE))


def DrawPiece(screen, board, loaded_pieces):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r, c]
            if piece != "--":
                screen.blit(
                    loaded_pieces[piece], pyg.Rect(c * SIZE, r * SIZE, SIZE, SIZE)
                )


def drawMoveLog(screen, state):
    log_rect = pyg.Rect(WIDTH, 0, PANEL_WIDTH, PANEL_HEIGHT)
    pyg.draw.rect(screen, BLACK, log_rect)
    move_log = state.moveLog
    move_text = []
    for i in range(0, len(move_log), 2):
        mstring = f"{i//2+1}, {move_log[i]} "
        if i + 1 < len(move_log):
            mstring += str(move_log[i + 1])
        move_text.append(mstring)
    movesPerRow = 3
    padding = 5
    linespacing = 3
    textY = padding

    for i in range(0, len(move_text), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(move_text):
                text += move_text[i + j] + " "
        font = pyg.font.SysFont("Arial", 15, False, False)
        textobj = font.render(text, False, WHITE)
        textlocation = log_rect.move(padding, textY)
        screen.blit(textobj, textlocation)
        textY += textobj.get_height() + linespacing


def animatemove(move, screen, board, clock, size, loaded_pieces):
    global colors

    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol

    fps = 3
    frameCount = (abs(dR) + abs(dC)) * fps

    for frame in range(frameCount + 1):
        r, c = (
            move.startRow + dR * frame / frameCount,
            move.startCol + dC * frame / frameCount,
        )

        DrawBoard(screen)
        DrawPiece(screen, board, loaded_pieces)

        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = pyg.Rect(move.endCol * size, move.endRow * size, size, size)
        pyg.draw.rect(screen, color, endSquare)

        if move.pieceCaptured != "--":
            if move.epMove:
                epRow = (
                    (move.endRow + 1)
                    if move.pieceCaptured[0] == "b"
                    else move.endRow - 1
                )
                endSquare = pyg.Rect(move.endCol * size, epRow * size, size, size)

            screen.blit(loaded_pieces[move.pieceCaptured], endSquare)

        screen.blit(
            loaded_pieces[move.pieceMoved], pyg.Rect(c * size, r * size, size, size)
        )
        pyg.display.flip()
        clock.tick(60)
