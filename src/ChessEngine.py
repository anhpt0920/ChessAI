"""
This class is responsible for storing all the information about the current state of o chess ga•e. It will also be
responsible for determining the valid moves at the current state. It will also keep a move log.
"""
PIECES = {"bP", "bR", "bQ", "wP", "wR", "wQ"}


class GameState:
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]

        self.moveFunctions = {
            "P": self.getPawnMoves,
            "R": self.getRockMoves,
            "N": self.getKnightMoves,
            "B": self.getBishopMoves,
            "Q": self.getQueenMoves,
            "K": self.getKingMoves,
        }

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.draw = False

        # Coordinates for the en passant possible square
        self.enpassantPossible = ()

        # Current castlingright
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [
            CastleRights(
                self.currentCastlingRight.wks,
                self.currentCastlingRight.bks,
                self.currentCastlingRight.wqs,
                self.currentCastlingRight.bqs,
            )
        ]

    def getAllPossibleMoves(self):
        moves = []

        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                piece = self.board[r][c]
                turn = piece[0]

                if (turn == "w" and self.whiteToMove) or (
                    turn == "b" and not self.whiteToMove
                ):
                    self.moveFunctions[piece[1]](r, c, moves)

        return moves

    """
    All moves considering checks
    """

    def getValidMoves(self):
        # for log in self.castleRightsLog:
        #     print(log.wks, log.wqs, log.bks, log.bqs, end=", ")
        # print()
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(
            self.currentCastlingRight.wks,
            self.currentCastlingRight.bks,
            self.currentCastlingRight.wqs,
            self.currentCastlingRight.bqs,
        )
        # 1.) Generate all possible move
        moves = self.getAllPossibleMoves()

        if self.whiteToMove:
            self.getCastleMoves(
                self.whiteKingLocation[0], self.whiteKingLocation[1], moves
            )
        else:
            self.getCastleMoves(
                self.blackKingLocation[0], self.blackKingLocation[1], moves
            )

        # 2.) for each move, make the move
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])

            # 3.) generate all opponent's moves, see if they attack your king
            # 4.) for each of your opponent's move, see if they attack your king
            self.whiteToMove = not self.whiteToMove
            if self.incheck():
                moves.remove(moves[i])
            # 5.) if they attack your king, not a valid move
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        if len(moves) == 0:
            if self.incheck():
                self.checkMate = True
                # print("Check mate!!!")
            else:
                self.staleMate = True
                # print("Stale mate!!!")
        
        # Insufficient mating material
        piece_counts = { "wP": 0, "wR": 0, "wN": 0, "wB": 0, "wQ": 0, "wK": 0, "bP": 0, "bR": 0, "bN": 0, "bB": 0, "bQ": 0, "bK": 0,}

        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                if self.board[r][c] != "--":
                    piece_counts[self.board[r][c]] += 1

        # if not self.draw:
        # Check for insufficient material conditions
        if sum(piece_counts.values()) == 2:
            self.draw = True
        elif (sum(piece_counts.values()) == 3) and (
            piece_counts["bB"] == 1
            or piece_counts["bN"] == 1
            or piece_counts["wB"] == 1
            or piece_counts["wN"] == 1
        ):
            self.draw = True
        elif sum(piece_counts.values()) == 4 and (
            (piece_counts["bB"] == 1 and piece_counts["wN"] == 1)
            or (piece_counts["wB"] == 1 and piece_counts["bN"] == 1)
            or (piece_counts["bN"] == 2)
            or (piece_counts["wN"] == 2)
        ):
            self.draw = True

        # print(piece_counts)
        # End of insufficient

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastleRights
        return moves

    """
    Determine if the current player is in check
    """

    def incheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(
                self.whiteKingLocation[0], self.whiteKingLocation[1]
            )
        else:
            return self.squareUnderAttack(
                self.blackKingLocation[0], self.blackKingLocation[1]
            )

    """
    All move without considering checks
    """

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    """
    Take a move as a parameter and execute it (not special move like: en-passant, castling or promotion)
    """

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved

        # Display moves in the game
        self.moveLog.append(move)

        # Switch turn
        self.whiteToMove = not self.whiteToMove

        # Update the king's location if moved
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

        # enpassant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"

        # update enpassantPossible variable
        # Only 2 square advances
        if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        # castle move
        if move.isCastleMove:
            # King side castle
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][
                    move.endCol + 1
                ]
                self.board[move.endRow][move.endCol + 1] = "--"
            # Queen side castle
            else:
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][
                    move.endCol - 2
                ]
                self.board[move.endRow][move.endCol - 2] = "--"

        # update castling rights - whenever it is a rook or a king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(
            CastleRights(
                self.currentCastlingRight.wks,
                self.currentCastlingRight.bks,
                self.currentCastlingRight.wqs,
                self.currentCastlingRight.bqs,
            )
        )

    """
    Undo last move made
    """

    def undoMove(self):
        # Check if moveLog is empty
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured

            # Switch turn
            self.whiteToMove = not self.whiteToMove

            # Update the king's location if moved
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

            # Undo enpassant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)

            # Undo 2 squares pawn advance
            if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()

            # Undo castling rights
            self.castleRightsLog.pop()  # get rid of the new castle rights from the move we are undoing
            newRights = self.castleRightsLog[-1]
            self.currentCastlingRight = CastleRights(
                newRights.wks, newRights.bks, newRights.wqs, newRights.bqs
            )

            # Undo castle move
            if move.isCastleMove:
                # King side castle
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][
                        move.endCol - 1
                    ]
                    self.board[move.endRow][move.endCol - 1] = "--"
                # Queen side castle
                else:
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][
                        move.endCol + 1
                    ]
                    self.board[move.endRow][move.endCol + 1] = "--"

            self.checkMate = False
            self.staleMate = False

    """
    Retrieve all moves in the provided direction.
    """

    def getMovesInDirections(self, r, c, moves, directions):
        for dr, dc in directions:
            new_r, new_c = r + dr, c + dc
            while 0 <= new_r < 8 and 0 <= new_c < 8:
                new_pos = self.board[new_r][new_c]
                if new_pos == "--" or new_pos[0] != self.board[r][c][0]:
                    moves.append(Move((r, c), (new_r, new_c), self.board))
                    if new_pos != "--" and new_pos[0] != self.board[r][c][0]:
                        break
                    new_r += dr
                    new_c += dc
                else:
                    break

    """
    Retrieve one move in each provided direction.
    """

    def getOneMoveInDirections(self, r, c, moves, directions):
        for dr, dc in directions:
            new_r, new_c = r + dr, c + dc
            if (
                0 <= new_r < 8
                and 0 <= new_c < 8
                and self.board[new_r][new_c][0] != self.board[r][c][0]
            ):
                moves.append(Move((r, c), (new_r, new_c), self.board))

    """
    Get all the pawn moves for the pawn located at row, col and add these moves to the list
    """

    def getPawnMoves(self, r, c, moves):
        whiteTurn = self.whiteToMove
        # Define the direction of pawn moves based on the player's color
        direction = -1 if whiteTurn else 1

        # Check the square in front of the pawn
        if self.board[r + direction][c] == "--":
            moves.append(Move((r, c), (r + direction, c), self.board))
            # Check two squares ahead for the initial move
            if ((r == 6 and whiteTurn) or (r == 1 and not whiteTurn)) and self.board[
                r + 2 * direction
            ][c] == "--":
                moves.append(Move((r, c), (r + 2 * direction, c), self.board))

        # Check for capturing moves to the left and right
        for dc in [-1, 1]:
            new_c = c + dc
            if 0 <= new_c < 8:
                target_piece = self.board[r + direction][new_c]
                if target_piece != "--" and target_piece[0] != self.board[r][c][0]:
                    moves.append(Move((r, c), (r + direction, new_c), self.board))
                elif (r + direction, new_c) == self.enpassantPossible:
                    moves.append(
                        Move(
                            (r, c),
                            (r + direction, new_c),
                            self.board,
                            isEnpassantMove=True,
                        )
                    )

    """
    Get all the rock moves for the rock located at row, col and add these moves to the list
    """

    def getRockMoves(self, r, c, moves):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        self.getMovesInDirections(r, c, moves, directions)

    """
    Get all the bishop moves for the bishop located at row, col and add these moves to the list
    """

    def getBishopMoves(self, r, c, moves):
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        self.getMovesInDirections(r, c, moves, directions)

    """
    Get all the queen moves for the queen located at row, col and add these moves to the list
    """

    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r, c, moves)
        self.getRockMoves(r, c, moves)

    """
    Get all the knight moves for the knight located at row, col and add these moves to the list
    """

    def getKnightMoves(self, r, c, moves):
        directions = [
            (-1, -2),
            (-1, 2),
            (1, -2),
            (1, 2),
            (-2, -1),
            (-2, 1),
            (2, -1),
            (2, 1),
        ]
        self.getOneMoveInDirections(r, c, moves, directions)

    """
    Get all the king moves for the king located at row, col and add these moves to the list
    """

    def getKingMoves(self, r, c, moves):
        directions = [
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        ]
        self.getOneMoveInDirections(r, c, moves, directions)

    """
    Generate all valid castle moves for the king at(r, c) and add them to the list of moves
    """

    def getCastleMoves(self, r, c, moves):
        direction = -1 if self.whiteToMove else 1
        if self.squareUnderAttack(r, c) or (self.board[r + direction][c][1] == "P"):
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or (
            not self.whiteToMove and self.currentCastlingRight.bks
        ):
            self.getKingSideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (
            not self.whiteToMove and self.currentCastlingRight.bqs
        ):
            self.getQueenSideCastleMoves(r, c, moves)

    """
    Generate all valid king side castle moves for the king at(r, c) and add them to the list of moves
    """

    def getKingSideCastleMoves(self, r, c, moves):
        if (
            self.board[r][c + 1] == "--"
            and self.board[r][c + 2] == "--"
            and self.board[r][c + 3][1] == "R"
        ):
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(
                r, c + 2
            ):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    """
    Generate all valid queen side castle moves for the king at(r, c) and add them to the list of moves
    """

    def getQueenSideCastleMoves(self, r, c, moves):
        if (
            self.board[r][c - 1] == "--"
            and self.board[r][c - 2] == "--"
            and self.board[r][c - 3] == "--"
            and self.board[r][c - 4][1] == "R"
        ):
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(
                r, c - 2
            ):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))

    """
    Update the castle rights given the move
    """

    def updateCastleRights(self, move):
        if move.pieceMoved == "wK":
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False

        # If a rook is captured
        if move.pieceCaptured == "wR":
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceCaptured == "bR":
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.bks = False


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    # Represent chess board Ranks and Files (Row and Column in programing context)
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(
        self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False
    ):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        # Pawn promotion
        self.isPawnPromotion = (self.pieceMoved == "wP" and self.endRow == 0) or (
            self.pieceMoved == "bP" and self.endRow == 7
        )

        # En passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wP" if self.pieceMoved == "bP" else "bP"

        # Castle move
        self.isCastleMove = isCastleMove

        self.isCapture = self.pieceCaptured != "--"
        self.moveID = (
            self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        )
        # print(self.moveID)

    """
    Overriding the equals method
    """

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self, moveLog):
        # Can be modify to show real chess notation
        return "" if moveLog == None else moveLog[len(moveLog)-1]
        # return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    # overiding the str() function
    def __str__(self):
        # Castle move
        if self.isCastleMove:
            return "O-O" if self.endCol == 6 else "O-O-O"

        endSquare = self.getRankFile(self.endRow, self.endCol)

        # Pawn moves
        if self.pieceMoved[1] == "P":
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare

        # Pawn promotion

        # Same piece to one square

        # Check and checkmate

        # Piece moves
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += "x"
        return moveString + endSquare
