import numpy as np


class State:
    def __init__(self):
        self.board = np.array(
            [
                ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
                ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
                ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
            ])

        self.whitesturn = True
        self.moveLog = []
        self.currCastleRights = castlerights(True, True, True, True)
        self.castleLog = [castlerights(self.currCastleRights.wks, self.currCastleRights.bks,
                                       self.currCastleRights.wqs, self.currCastleRights.bqs)]
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.epPossible = ()
        self.moveFuncs = {
            "p": self.getPawnMoves,
            "R": self.getRookMoves,
            "N": self.getKnightMoves,
            "K": self.getKingMoves,
            "B": self.getBishopMoves,
            "Q": self.getQueenMoves,
        }

    def prntcastlerights(self):
        for log in self.castleLog:
            print(log.wks, log.wqs, log.bks, log.bqs, end=', ')

    def make_move(self, move):

        self.board[move.startRow, move.startCol] = "--"
        self.board[move.endRow, move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whitesturn = not self.whitesturn

        if move.isPawnPromotion:
            self.board[move.endRow, move.endCol] = move.pieceMoved[0] + 'Q'

        if move.epMove:
            self.board[move.startRow, move.endCol] = '--'

        if move.pieceMoved[1] == 'p' and abs(move.startRow-move.endRow) == 2:
            self.epPossible = ((move.startRow+move.endRow)//2, move.startCol)
        else:
            self.epPossible = ()

        if move.castlemove:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow, move.endCol -
                           1] = self.board[move.endRow, move.endCol+1]
                self.board[move.endRow, move.endCol+1] = '--'

            else:
                self.board[move.endRow, move.endCol +
                           1] = self.board[move.endRow, move.endCol-2]
                self.board[move.endRow, move.endCol-2] = '--'

        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        self.updatecastlerights(move)
        self.castleLog.append(castlerights(self.currCastleRights.wks, self.currCastleRights.bks,
                              self.currCastleRights.wqs, self.currCastleRights.bqs))

    def undo_move(self):
        if len(self.moveLog) > 0:
            move = self.moveLog.pop()
            self.board[move.startRow, move.startCol] = move.pieceMoved
            self.board[move.endRow, move.endCol] = move.pieceCaptured
            self.whitesturn = not self.whitesturn

            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

            if move.epMove:
                self.board[move.endRow, move.endCol] = '--'
                self.board[move.startRow, move.endCol] = move.pieceCaptured
                self.epPossible = (move.endRow, move.endCol)

            if move.pieceMoved[1] == 'p' and abs(move.startRow-move.endRow) == 2:
                self.epPossible = ()

            self.castleLog.pop()
            newRights = self.castleLog[-1]
            self.currCastleRights = castlerights(
                newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)

            if move.castlemove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow, move.endCol +
                               1] = self.board[move.endRow, move.endCol-1]
                    self.board[move.endRow, move.endCol-1] = '--'
                else:
                    self.board[move.endRow, move.endCol -
                               2] = self.board[move.endRow, move.endCol+1]
                    self.board[move.endRow, move.endCol+1] = '--'

    def updatecastlerights(self, move):

        if move.pieceMoved == 'wK':
            self.currCastleRights.wks = False
            self.currCastleRights.wqs = False

        elif move.pieceMoved == 'bK':
            self.currCastleRights.bks = False
            self.currCastleRights.bqs = False

        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currCastleRights.wqs = False
                elif move.startCol == 7:
                    self.currCastleRights.wks = False

        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currCastleRights.bqs = False
                elif move.startCol == 7:
                    self.currCastleRights.bks = False

    def FilterValidMoves(self):
        moves = self.getAllPossibleMoves()
        tempEpPossible = self.epPossible
        tempcastleRights = castlerights(
            self.currCastleRights.wks, self.currCastleRights.bks, self.currCastleRights.wqs, self.currCastleRights.bqs)

        if self.whitesturn:
            self.getCastleMoves(
                self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(
                self.blackKingLocation[0], self.blackKingLocation[1], moves)

        for i in range(len(moves)-1, -1, -1):
            self.make_move(moves[i])
            self.whitesturn = not self.whitesturn
            if self.inCheck():
                moves.remove(moves[i])
            self.whitesturn = not self.whitesturn
            self.undo_move()

        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True

        else:
            self.checkmate = False
            self.stalemate = False

        self.epPossible = tempEpPossible
        self.currCastleRights = tempcastleRights
        return moves

    def inCheck(self):
        if self.whitesturn:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, r, c):
        self.whitesturn = not self.whitesturn
        oppMoves = self.getAllPossibleMoves()
        self.whitesturn = not self.whitesturn
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    def getAllPossibleMoves(self):
        moves = []

        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r, c][0]
                criteria = [
                    (turn == "w" and self.whitesturn),
                    (turn == "b" and not self.whitesturn),
                ]

                if any(criteria):
                    piece = self.board[r, c][1]
                    self.moveFuncs[piece](r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        if self.whitesturn:
            if self.board[r - 1, c] == "--":
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2, c] == "--":
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r - 1, c - 1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r-1, c-1) == self.epPossible:
                    moves.append(Move((r, c), (r - 1, c - 1),
                                 self.board, epMove=True))

            if c + 1 <= 7:
                if self.board[r - 1, c + 1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r-1, c+1) == self.epPossible:
                    moves.append(
                        Move((r, c), (r-1, c+1), self.board, epMove=True))

        else:
            if self.board[r + 1, c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2, c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r + 1, c - 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r+1, c-1) == self.epPossible:
                    moves.append(
                        Move((r, c), (r+1, c-1), self.board, epMove=True))
            if c + 1 <= 7:
                if self.board[r + 1, c + 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r+1, c+1) == self.epPossible:
                    moves.append(
                        Move((r, c), (r+1, c+1), self.board, epMove=True))

    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        eColor = "b" if self.whitesturn else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i

                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow, endCol]
                    if endPiece == "--":
                        moves.append(
                            Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == eColor:
                        moves.append(
                            Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, 1), (-1, -1), (1, -1), (1, 1))
        eColor = "b" if self.whitesturn else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i

                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow, endCol]
                    if endPiece == "--":
                        moves.append(
                            Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == eColor:
                        moves.append(
                            Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)

    def getKnightMoves(self, r, c, moves):
        directions = (
            (-2, 1),
            (-2, -1),
            (-1, 2),
            (-1, -2),
            (1, -2),
            (1, 2),
            (2, -1),
            (2, 1),
        )
        eColor = "w" if self.whitesturn else "b"
        for m in directions:
            endRow = r + m[0]
            endCol = c + m[1]

            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow, endCol]
                if endPiece[0] != eColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getKingMoves(self, r, c, moves):
        directions = (
            (-1, 1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        )
        allyColor = "w" if self.whitesturn else "b"

        for i in range(8):
            endRow = r + directions[i][0]
            endCol = c + directions[i][1]

            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow, endCol]
                if endPiece != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return

        if (self.whitesturn and self.currCastleRights.wks) or (not self.whitesturn and self.currCastleRights.bks):
            self.getKSCastleMoves(r, c, moves)
        if (self.whitesturn and self.currCastleRights.wqs) or (not self.whitesturn and self.currCastleRights.bqs):
            self.getQSCastleMoves(r, c, moves)

    def getKSCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(
                    Move((r, c), (r, c+2), self.board, castlemove=True))

    def getQSCastleMoves(self, r, c, moves):
        if self.board[r, c-1] == '--' and self.board[r, c-2] == '--' and self.board[r, c-3]:
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(
                    Move((r, c), (r, c-2), self.board, castlemove=True))


class castlerights:
    def __init__(self, wks, bks, wqs, bqs):

        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5,
                   "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2,
                   "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, start_sq, end_sq, board, epMove=False, castlemove=False):
        self.startRow = start_sq[0]
        self.startCol = start_sq[1]
        self.endRow = end_sq[0]
        self.endCol = end_sq[1]

        self.pieceMoved = board[self.startRow, self.startCol]
        self.pieceCaptured = board[self.endRow, self.endCol]
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (
            self.pieceMoved == 'bp' and self.endRow == 7)
        self.epMove = epMove
        if self.epMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'

        self.castlemove = castlemove

        self.moveid = (
            self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        )

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveid == other.moveid
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(
            self.endRow, self.endCol
        )

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
