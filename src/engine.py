from zobrist import Zobrist
import numpy as np

ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
rowsToRanks = {v: k for k, v in ranksToRows.items()}
filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
colsToFiles = {v: k for k, v in filesToCols.items()}


class State:

    '''
        - Terribly slow but relatively simple engine state, this is written purely for simpliciity
        - Uses 2d arrays, which is slow, hence me developing bitboards
        - Gonna have to optimize this soon because the nps is prolly 100 per seconds 
    '''

    def __init__(self):
        self.ZobristClass: Zobrist = Zobrist()
        self.currCastleRights = castlerights(False, False, False, False)
        self.pieceCount: dict = {
            'wK': 0,
            'wQ': 0,
            'wR': 0,
            'wB': 0,
            'wN': 0,
            'wp': 0,

            'bK': 0,
            'bQ': 0,
            'bR': 0,
            'bB': 0,
            'bN': 0,
            'bp': 0,
        }
        
        (
            self.board,
            self.castleLog,
            self.whitesturn,
            self.currCastleRights,
            self.init_board_pieces,
            self.epPossible,
            self.start_fen,
            self.ZobristKey,
        ) = self.loadStartPosition()

        self.moveLog: list = []
        self.oppPawnAttackMap: dict = {}
        self.oppPawnAttackMap['White'], self.oppPawnAttackMap['Black'] = [], []
        self.boardLog: list = [self.board]
        self.checkmate: bool = False
        self.stalemate: bool = False
        self.epLog: list = [self.epPossible]
        self.game_over: bool = False
        self.kingisCastled: dict = {}
        self.kingisCastled['w'], self.kingisCastled['b'] = False, False
        self.RepetitionPositionHistory: list = []
        self.moveFuncs: dict = {
            "p": self.getPawnMoves,
            "R": self.getRookMoves,
            "N": self.getKnightMoves,
            "K": self.getKingMoves,
            "B": self.getBishopMoves,
            "Q": self.getQueenMoves,
        }

    def perft_pseudo_moves(self, depth):
        move_list = self.FilterValidMoves()
        nodes = 0

        if depth == 0:
            return 1

        for move in move_list:
            self.make_move(move)
            if self.inCheck():
                nodes += self.perft_pseudo_moves(depth - 1)
            self.undo_move()

        return nodes

    def bulk_count(self, depth):
        n_moves = self.FilterValidMoves()
        nodes = 0

        if depth == 1:
            return len(n_moves)

        for move in n_moves:
            self.make_move(move)
            nodes += self.bulk_count(depth - 1)
            self.undo_move()

        return nodes

    def moveGenerationTest(self, depth):

        def sort_criteria(move):
            return move.getChessNotation(True)

        nodes = self.bulk_count(depth)
        validMoves = self.FilterValidMoves()
        validMoves.sort(key=sort_criteria)

        for move in validMoves:
            print(f'{move.getChessNotation(True)}: {nodes//len(validMoves)}')

        print(f'Total: {nodes}')

    def loadStartPosition(self):
        fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        return self.fenToPos(fen)

    def loadCustomPosition(self):
        fen = '3k4/8/8/8/8/4KRR1/8/8 w - - 0 1' #insert custom position
        return self.fenToPos(fen)


    def fenToPos(self, fen):
        self.init_board_pieces = [] 
        self.board = np.array(
            [
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
            ]
        )

        pieceTypeFromSymbol = {
            "K": "K",
            "P": "P",
            "N": "N",
            "B": "B",
            "Q": "Q",
            "R": "R",
        }

        fen_board:str = fen.split()[0]
        row, col = 0, 0

        for symbol in fen_board:
            if symbol == "/":
                col = 0
                row += 1
            else:
                if symbol.isdigit():
                    col += int(symbol)
                else:
                    piece_color = "w" if symbol.isupper() else "b"
                    pieceType = pieceTypeFromSymbol[symbol.upper()]

                    if pieceType.lower() == "p":
                        pieceType = pieceType.lower()

                    self.board[row, col] = piece_color + pieceType
                    self.init_board_pieces.append(piece_color + pieceType)

                    if pieceType == "K":
                        if piece_color == "w":
                            self.whiteKingLocation = (row, col)
                        elif piece_color == "b":
                            self.blackKingLocation = (row, col)

                    self.pieceCount[piece_color + pieceType] += 1

                    col += 1

        fen_turn = fen.split()[1]
        self.whitesturn = True if fen_turn == "w" else False

        fen_castle_rights:str = fen.split()[2]

        for symbol in fen_castle_rights:
            if symbol != "-":
                if symbol == 'K':
                    self.currCastleRights = castlerights(
                        True, self.currCastleRights.bks, self.currCastleRights.wqs, self.currCastleRights.bqs
                    )
                elif symbol == 'Q':
                    self.currCastleRights = castlerights(
                        self.currCastleRights.wks, self.currCastleRights.bks, True, self.currCastleRights.bqs
                    )
                elif symbol == 'k':
                    self.currCastleRights = castlerights(
                        self.currCastleRights.wks, True, self.currCastleRights.wqs, self.currCastleRights.bqs
                    )
                elif symbol == 'q':
                    self.currCastleRights = castlerights(
                        self.currCastleRights.wks, self.currCastleRights.bks, self.currCastleRights.wqs, True
                    )
            else:
                self.currCastleRights = castlerights(False, False, False, False)
                break

        self.castleLog = [
            castlerights(
                self.currCastleRights.wks,
                self.currCastleRights.bks,
                self.currCastleRights.wqs,
                self.currCastleRights.bqs,
            )
        ]

        enpassantTarget = fen.split()[3]
        if enpassantTarget == '-':
            self.epPossible = ()
        else:
            self.epPossible = (
                ranksToRows[enpassantTarget[1]], filesToCols[enpassantTarget[0]])

        ZobristKey = self.ZobristClass.CalculateZobristKey(self)

        return (
            self.board,
            self.castleLog,
            self.whitesturn,
            self.currCastleRights,
            self.init_board_pieces,
            self.epPossible,
            fen,
            ZobristKey
        )

    def posToFen(self):
        fen = ""
        emptySpace = 0

        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                square = self.board[row, col]
                pieceSide, pieceType = square[0], square[1]

                if pieceSide == 'w':
                    if emptySpace > 0:
                        fen += (str(emptySpace))
                        emptySpace = 0
                    fen += (pieceType.upper())
                elif pieceSide == 'b':
                    if emptySpace > 0:
                        fen += (str(emptySpace))
                        emptySpace = 0
                    fen += (pieceType.lower())
                else:
                    emptySpace += 1

            if emptySpace > 0:
                fen += (str(emptySpace))
                emptySpace = 0

            fen += fen.join('/')

        fen = fen[:-1]
        return fen

    def prntcastlerights(self):
        last_log = self.castleLog[-1]
        print(last_log.wks, last_log.wqs, last_log.bks, last_log.bqs)
        print("\n")

    def prntboard(self):
        print(self.board, "\n")

    def prnt_status(self):
        print(self.whiteKingLocation)
        print(self.blackKingLocation)

    def make_move(self, move, inSearch=False):

        self.board[move.startRow, move.startCol] = "--"
        self.board[move.endRow, move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whitesturn = not self.whitesturn

        if move.isCapture:
            self.pieceCount[move.pieceCaptured] -= 1

        if move.isPawnPromotion:
            self.board[move.endRow, move.endCol] = move.pieceMoved[0] + "Q"
            self.pieceCount[move.pieceMoved[0]+'Q'] += 1
            self.pieceCount[move.pieceMoved[0]+'p'] -= 1

        if move.epMove:
            self.board[move.startRow, move.endCol] = "--"

        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
            self.epPossible = (
                (move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.epPossible = ()

        if move.castlemove and move.pieceMoved[1] == "K":
            try:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow, move.endCol - 1] = self.board[
                        move.endRow, move.endCol + 1
                    ]
                    self.board[move.endRow, move.endCol + 1] = "--"
                    if move.pieceMoved == "wK":
                        self.whiteKingLocation = (move.endRow, move.endCol)
                        self.kingisCastled['w'] = True
                    elif move.pieceMoved == "bK":
                        self.bkacKingLocation = (move.endRow, move.endCol)
                        self.kingisCastled['b'] = True
                else:
                    self.board[move.endRow, move.endCol + 1] = self.board[
                        move.endRow, move.endCol - 2
                    ]
                    self.board[move.endRow, move.endCol - 2] = "--"
                    if move.pieceMoved == "wK":
                        self.whiteKingLocation = (move.endRow, move.endCol)
                        self.kingisCastled['w'] = True
                    elif move.pieceMoved == "bK":
                        self.blackKingLocation = (move.endRow, move.endCol)
                        self.kingisCastled['b'] = True
            except Exception as e:
                print(f"{move} is the cause of the error: {e}")
            finally:
                pass

        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        self.epLog.append(self.epPossible)
        self.boardLog.append(self.board)

        self.updatecastlerights(move)
        self.castleLog.append(
            castlerights(
                self.currCastleRights.wks,
                self.currCastleRights.bks,
                self.currCastleRights.wqs,
                self.currCastleRights.bqs,
            )
        )

        self.ZobristKey = self.ZobristClass.CalculateZobristKey(self)

        if not inSearch:
            if move.pieceMoved[1] == 'p' or move.pieceCaptured != '--':
                self.RepetitionPositionHistory.clear()
            else:
                self.RepetitionPositionHistory.append(self.ZobristKey)

    def undo_move(self, inSearch=False):
        if len(self.moveLog) > 0:
            move = self.moveLog.pop()
            self.board[move.startRow, move.startCol] = move.pieceMoved
            self.board[move.endRow, move.endCol] = move.pieceCaptured
            self.whitesturn = not self.whitesturn

            if move.isPawnPromotion:
                self.pieceCount[move.pieceMoved[0]+'Q'] -= 1
                self.pieceCount[move.pieceMoved[0]+'p'] += 1

            if move.isCapture:
                self.pieceCount[move.pieceCaptured] += 1

            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

            if move.epMove:
                self.board[move.endRow, move.endCol] = "--"
                self.board[move.startRow, move.endCol] = move.pieceCaptured

            self.epLog.pop()
            self.epPossible = self.epLog[-1]

            self.boardLog.pop()

            self.castleLog.pop()
            newRights = self.castleLog[-1]
            self.currCastleRights = castlerights(
                newRights.wks, newRights.bks, newRights.wqs, newRights.bqs
            )

            if move.castlemove:
                try:
                    if move.endCol - move.startCol == 2:
                        self.board[move.endRow, move.endCol + 1] = self.board[
                            move.endRow, move.endCol - 1
                        ]
                        self.board[move.endRow, move.endCol - 1] = "--"
                        if move.pieceMoved == 'wK':
                            self.kingisCastled['w'] = False
                        elif move.pieceMoved == 'bK':
                            self.kingisCastled['b'] = False
                    else:
                        self.board[move.endRow, move.endCol - 2] = self.board[
                            move.endRow, move.endCol + 1
                        ]
                        self.board[move.endRow, move.endCol + 1] = "--"
                        if move.pieceMoved == 'wK':
                            self.kingisCastled['w'] = False
                        elif move.pieceMoved == 'bK':
                            self.kingisCastled['b'] = False
                except Exception as e:
                    print(f"{move} is the cause of the error: {e}")
                finally:
                    pass

        self.checkmate = False
        self.stalemate = False

        self.ZobristKey = self.ZobristClass.CalculateZobristKey(self)

        if not inSearch and len(self.RepetitionPositionHistory) > 0:
            self.RepetitionPositionHistory.pop()

    def updatecastlerights(self, move):

        if move.pieceMoved == "wK" or (self.whiteKingLocation != (7, 4)):
            self.currCastleRights.wks = False
            self.currCastleRights.wqs = False

        elif move.pieceMoved == "bK" or (self.blackKingLocation != (0, 4)):
            self.currCastleRights.bks = False
            self.currCastleRights.bqs = False

        if "wR" in self.init_board_pieces:
            if move.pieceMoved == "wR":
                if move.startRow == 7:
                    if move.startCol == 0:
                        self.currCastleRights.wqs = False
                    elif move.startCol == 7:
                        self.currCastleRights.wks = False
        else:
            self.currCastleRights.wqs = False
            self.currCastleRights.wks = False

        if "bR" in self.init_board_pieces:
            if move.pieceMoved == "bR":
                if move.startRow == 0:
                    if move.startCol == 0:
                        self.currCastleRights.bqs = False
                    elif move.startCol == 7:
                        self.currCastleRights.bks = False
        else:
            self.currCastleRights.bqs = False
            self.currCastleRights.bks = False

        # if 'wR' in self.init_board_pieces:
        if move.pieceCaptured == "wR":
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currCastleRights.wqs = False
                elif move.endCol == 7:
                    self.currCastleRights.wks = False

        # if 'bR' in self.init_board_pieces:
        if move.pieceCaptured == "bR":
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currCastleRights.bqs = False
                elif move.endCol == 7:
                    self.currCastleRights.bks = False

    def FilterValidMoves(self):
        moves:list = self.getAllPossibleMoves()
        tempEpPossible:tuple = self.epPossible
        tempcastleRights:castlerights = castlerights(
            self.currCastleRights.wks,
            self.currCastleRights.bks,
            self.currCastleRights.wqs,
            self.currCastleRights.bqs,
        )
        for i in range(len(moves) - 1, -1, -1):
            self.make_move(moves[i], inSearch=True)
            self.whitesturn = not self.whitesturn
            if self.inCheck(): moves.remove(moves[i])
            self.whitesturn = not self.whitesturn
            self.undo_move(inSearch=True)

        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
            self.game_over = True

        if self.whitesturn:
            if self.whiteKingLocation == (7, 4):
                if self.currCastleRights.wks or self.currCastleRights.wqs:
                    self.getCastleMoves(
                        self.whiteKingLocation[0], self.whiteKingLocation[1], moves
                    )
        else:
            if self.blackKingLocation == (0, 4):
                if self.currCastleRights.bks or self.currCastleRights.bqs:
                    self.getCastleMoves(
                        self.blackKingLocation[0], self.blackKingLocation[1], moves
                    )

        self.epPossible = tempEpPossible
        self.currCastleRights = tempcastleRights

        return moves

    def GenerateCaptures(self):
        moves = self.FilterValidMoves()
        for i in range(len(moves) - 1, -1, -1):
            if moves[i].pieceCaptured == '--': moves.remove(moves[i])
        return moves

    def inCheck(self):
        if self.whitesturn:
            return self.squareUnderAttack(
                self.whiteKingLocation[0], self.whiteKingLocation[1]
            )
        else:
            return self.squareUnderAttack(
                self.blackKingLocation[0], self.blackKingLocation[1]
            )

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
        self.oppPawnAttackMap['Black' if self.whitesturn else 'White'] = []

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
                endSquare = (r - 1, c - 1)
                self.oppPawnAttackMap['Black'].append(endSquare)

                if self.board[r - 1, c - 1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))

                elif (r - 1, c - 1) == self.epPossible:
                    moves.append(Move((r, c), (r - 1, c - 1),
                                 self.board, epMove=True))

            if c + 1 <= 7:
                endSquare = (r - 1, c + 1)
                self.oppPawnAttackMap['Black'].append(endSquare)

                if self.board[r - 1, c + 1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))

                elif (r - 1, c + 1) == self.epPossible:
                    moves.append(Move((r, c), (r - 1, c + 1),
                                 self.board, epMove=True))

        else:

            if self.board[r + 1, c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2, c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))

            if c - 1 >= 0:
                endSquare = (r + 1, c - 1)
                self.oppPawnAttackMap['White'].append(endSquare)

                if self.board[r + 1, c - 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))

                elif (r + 1, c - 1) == self.epPossible:
                    moves.append(Move((r, c), (r + 1, c - 1),
                                 self.board, epMove=True))

            if c + 1 <= 7:
                endSquare = (r + 1, c + 1)
                self.oppPawnAttackMap['White'].append(endSquare)

                if self.board[r + 1, c + 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))

                elif (r + 1, c + 1) == self.epPossible:
                    moves.append(Move((r, c), (r + 1, c + 1),
                                 self.board, epMove=True))

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
            (-1, 0),
            (-1, 1),
            (-1, -1),
            (1, 0),
            (1, -1),
            (1, 1),
            (0, 1),
            (0, -1),
        )
        allyColor = "w" if self.whitesturn else "b"

        for i in range(8):
            endRow = r + directions[i][0]
            endCol = c + directions[i][1]

            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow, endCol]
                if endPiece[0] != allyColor:
                    chosen_move = Move((r, c), (endRow, endCol), self.board)
                    moves.append(chosen_move)
    
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return

        if (self.whitesturn and self.currCastleRights.wks) or (
            not self.whitesturn and self.currCastleRights.bks
        ):
            self.getKSCastleMoves(r, c, moves)

        if (self.whitesturn and self.currCastleRights.wqs) or (
            not self.whitesturn and self.currCastleRights.bqs
        ):
            self.getQSCastleMoves(r, c, moves)

    def getKSCastleMoves(self, r, c, moves):
        if (
            self.board[r][c + 1] == "--"
            and self.board[r][c + 2] == "--"
            and not self.squareUnderAttack(r, c + 1)
            and not self.squareUnderAttack(r, c + 2)
            and not self.inCheck()
        ):
            moves.append(Move((r, c), (r, c + 2), self.board, castlemove=True))

    def getQSCastleMoves(self, r, c, moves):
        if (
            self.board[r, c - 1] == "--"
            and self.board[r, c - 2] == "--"
            and self.board[r, c - 3] == "--"
            and not self.squareUnderAttack(r, c - 1)
            and not self.squareUnderAttack(r, c - 2)
            and not self.inCheck()
        ):
            moves.append(Move((r, c), (r, c - 2), self.board, castlemove=True))

    def ResetorInitialize(self):
        self.currCastleRights = castlerights(True, True, True, True)
        (
            self.board,
            self.castleLog,
            self.whitesturn,
            self.currCastleRights,
            self.init_board_pieces,
            self.epPossible,
            self.start_fen
        ) = self.loadStartPosition()

        self.moveLog = []
        self.oppPawnAttackMap = {}
        self.oppPawnAttackMap['White'], self.oppPawnAttackMap['Black'] = [], []
        self.boardLog = [self.board]
        self.checkmate = False
        self.stalemate = False
        self.epLog = [self.epPossible]
        self.game_over = False
        self.RepetitionPositionHistory = []
        self.moveFuncs = {
            "p": self.getPawnMoves,
            "R": self.getRookMoves,
            "N": self.getKnightMoves,
            "K": self.getKingMoves,
            "B": self.getBishopMoves,
            "Q": self.getQueenMoves,
        }


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
        self.endSquare = end_sq
        self.startSquare = start_sq

        self.pieceMoved = board[self.startRow, self.startCol]
        self.pieceCaptured = board[self.endRow, self.endCol]
        self.isPawnPromotion = (self.pieceMoved == "wp" and self.endRow == 0) or (
            self.pieceMoved == "bp" and self.endRow == 7
        )
        self.epMove = epMove
        if self.epMove:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"
        self.isCapture = self.pieceCaptured != "--"

        self.castlemove = castlemove

        self.moveid = (
            self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        )

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveid == other.moveid
        return False

    def getChessNotation(self, raw):
        if raw:
            if not self.isPawnPromotion:
                return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(
                    self.endRow, self.endCol
                )
            else:
                return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(
                    self.endRow, self.endCol
                ) + 'q'
        else:
            if self.castlemove:
                return "O-O" if self.endCol == 6 else "O-O-O"

            endSquare = self.getRankFile(self.endRow, self.endCol)
            if self.pieceMoved[1] == "p":
                if self.isCapture:
                    return self.colsToFiles[self.startCol] + "x" + endSquare
                else:
                    return endSquare

            mstring = self.pieceMoved[1]
            if self.isCapture:
                mstring += "x"

            return mstring + endSquare

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    def __str__(self):
        if self.castlemove:
            return "O-O" if self.endCol == 6 else "O-O-O"

        endSquare = self.getRankFile(self.endRow, self.endCol)
        if self.pieceMoved[1] == "p":
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare

        mstring = self.pieceMoved[1]
        if self.isCapture:
            mstring += "x"

        return mstring + endSquare


class Test:
    def __init__(self):
        self.state = State()

    def generationTest(self):
        print(self.state.moveGenerationTest(2))
