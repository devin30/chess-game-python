import enum
import os
from tkinter import PIESLICE
from typing import List

class PieceType(enum.IntEnum):
    NOPIECE = 0
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6

class Side(enum.Enum):
    NEUTRAL = 0
    WHITE = 1
    BLACK = 2

class BoardPiece:
    def __init__(self, piece: PieceType, color: Side):
        self.piece = piece
        self.color = color
        self.last_move = -1  # for special moves like castling
        self.pawn_move_two = False  # was last move a pawn moving two squares

    def remove(self):
        self.piece = PieceType.NOPIECE
        self.color = Side.NEUTRAL
        self.last_move = -1
        self.pawn_move_two = False

    def replace(from_piece: "BoardPiece", to_piece: "BoardPiece", move_num,
                pawn_move_two = False):
        to_piece.piece = from_piece.piece
        to_piece.color = from_piece.color
        to_piece.last_move = move_num
        to_piece.pawn_move_two = pawn_move_two
        from_piece.piece = PieceType.NOPIECE
        from_piece.color = Side.NEUTRAL
        from_piece.last_move = -1
        from_piece.pawn_move_two = False
    


class ChessInputError(Exception):
    pass

class ChessMoveError(Exception):
    pass
    
class Chess:
    BOARD_SIZE = 8
    # Starting Chessboard with 0,0 being bottom left square
    # first digit is row and second digit is file
    SETUP = [
        (0, 0, PieceType.ROOK, Side.WHITE),
        (0, 7, PieceType.ROOK, Side.WHITE),
        (0, 1, PieceType.KNIGHT, Side.WHITE),
        (0, 6, PieceType.KNIGHT, Side.WHITE),
        (0, 2, PieceType.BISHOP, Side.WHITE),
        (0, 5, PieceType.BISHOP, Side.WHITE),
        (0, 3, PieceType.QUEEN, Side.WHITE),
        (0, 4, PieceType.KING, Side.WHITE),
        (1, 0, PieceType.PAWN, Side.WHITE),
        (1, 1, PieceType.PAWN, Side.WHITE),
        (1, 2, PieceType.PAWN, Side.WHITE),
        (1, 3, PieceType.PAWN, Side.WHITE),
        (1, 4, PieceType.PAWN, Side.WHITE),
        (1, 5, PieceType.PAWN, Side.WHITE),
        (1, 6, PieceType.PAWN, Side.WHITE),
        (1, 7, PieceType.PAWN, Side.WHITE),
        (7, 0, PieceType.ROOK, Side.BLACK),
        (7, 7, PieceType.ROOK, Side.BLACK),
        (7, 1, PieceType.KNIGHT, Side.BLACK),
        (7, 6, PieceType.KNIGHT, Side.BLACK),
        (7, 2, PieceType.BISHOP, Side.BLACK),
        (7, 5, PieceType.BISHOP, Side.BLACK),
        (7, 3, PieceType.QUEEN, Side.BLACK),
        (7, 4, PieceType.KING, Side.BLACK),
        (6, 0, PieceType.PAWN, Side.BLACK),
        (6, 1, PieceType.PAWN, Side.BLACK),
        (6, 2, PieceType.PAWN, Side.BLACK),
        (6, 3, PieceType.PAWN, Side.BLACK),
        (6, 4, PieceType.PAWN, Side.BLACK),
        (6, 5, PieceType.PAWN, Side.BLACK),
        (6, 6, PieceType.PAWN, Side.BLACK),
        (6, 7, PieceType.PAWN, Side.BLACK),
    ]

    WHITE_PIECES = [' ', 'P', 'N', 'B', 'R', 'Q', 'K']
    BLACK_PIECES = [' ', 'p', 'n', 'b', 'r', 'q', 'k']
    STARTING_PLAYER = Side.WHITE

    def __init__(self):
        self.board: List[List[BoardPiece]]= [[],] * Chess.BOARD_SIZE
        self.squares = [[],] * Chess.BOARD_SIZE  # square colours
        self.turn: Side = Chess.STARTING_PLAYER
        self.move_num = 1

        for i in range(Chess.BOARD_SIZE):
            self.board[i] = [None,] * Chess.BOARD_SIZE
            for j in range(Chess.BOARD_SIZE):
                self.board[i][j] = BoardPiece(PieceType.NOPIECE, Side.NEUTRAL)
            self.squares[i] = [' ',] * Chess.BOARD_SIZE
            self.squares[i][(i % 2):Chess.BOARD_SIZE:2] = (
                ['#',] * ((Chess.BOARD_SIZE + i%2) // 2))

        # Set up default chessboard
        for piece_position in Chess.SETUP:
            (row, file, piece, color) = piece_position
            try:
                self.board[row][file] = BoardPiece(piece, color)
            except IndexError:
                # Do nothing if out of range
                pass

    def print_board(self):
        print("")

        # top of board
        print("  ", end="")
        for i in range(Chess.BOARD_SIZE):
            print("__", end="")
        print("_")
        
        # the board itself
        for row in range(Chess.BOARD_SIZE-1,-1,-1):
            print(f"{row+1} ", end="")
            for file, piece in enumerate(self.board[row]):
                print("|", end="")
                if piece.piece == PieceType.NOPIECE:
                    print(self.squares[row][file], end="")
                elif piece.color == Side.WHITE:
                    print(Chess.WHITE_PIECES[piece.piece], end="")
                elif piece.color == Side.BLACK:
                    print(Chess.BLACK_PIECES[piece.piece], end="")
                else:
                    assert(True)
            print("|")

        # bottom of board
        print("  ", end="")
        for i in range(Chess.BOARD_SIZE):
            print("~~", end="")
        print("~")

        print("  ", end="")
        for file_char in ['a','b','c','d','e','f','g','h']:
            print(f" {file_char}", end="")
        print("")
    
    def input_move(self):
        if self.turn == Side.WHITE:
            print("White to move:")
        else:
            print("Black to move:")

        while True:
            try:
                print("Enter position of piece to move (e.g. a1)")
                piece_pos = input(">>> ")
                (piece_row, piece_file) = Chess.parse_position(piece_pos)
                if (self.board[piece_row][piece_file].piece ==
                        PieceType.NOPIECE):
                    raise ChessInputError("No piece there!")
                if self.board[piece_row][piece_file].color != self.turn:
                    raise ChessInputError("Not your piece!")
            except ChessInputError as e:
                print(e)
                continue

            try:
                print("Enter position to move to")
                dest_pos = input(">>> ")
                (dest_row, dest_file) = Chess.parse_position(dest_pos)
            except ChessInputError as e:
                print(e)
                continue
        
            # Move piece
            try:
                self.make_move(piece_row, piece_file, dest_row, dest_file)
            except ChessMoveError as e:
                print(e)
                continue
            # check if pawn can be queened

            break
        
        if self.turn == Side.WHITE:
            self.turn = Side.BLACK
        else:
            self.turn = Side.WHITE
            self.move_num += 1
        
    
    def parse_position(input_text: str):
        # hardcoded to assume rank and file are one character each
        # TODO allow regex to catch sequence of letters followed by numbers
        if len(input_text) != 2:
            raise ChessInputError("Invalid position notation")
        file = ord(input_text[0]) - ord('a')
        if file < 0 or file >= Chess.BOARD_SIZE:
            raise ChessInputError("Invalid file notation")
        row = int(input_text[1]) - 1
        if row < 0 or row >= Chess.BOARD_SIZE:
            raise ChessInputError("Invalid row notation")
        return(row, file)

    def make_move(self, from_row, from_file, to_row, to_file):
        valid_move = False
        is_pawn_move_two = False

        # check from and to are not same square
        if (from_row == to_row and from_file == to_file):
            raise ChessMoveError("Cannot move to same square")

        # check own piece is not at destination
        move_piece = self.board[from_row][from_file]
        to_square = self.board[to_row][to_file]
        if (self.board[to_row][to_file].piece != PieceType.NOPIECE
                and move_piece.color == self.board[to_row][to_file].color):
            raise ChessMoveError("Cannot take own piece")

        black_pawn_row = Chess.BOARD_SIZE - 2
        row_diff = abs(to_row - from_row)
        file_diff = abs(to_file - from_file)

        # TODO verify that move doesn't put own king in check

        # special rules for each piece
        if move_piece.piece == PieceType.PAWN and self.turn == Side.WHITE:
            # White pawn
            # allow capture
            if (to_row == from_row+1
                    and file_diff == 1
                    and to_square.piece != PieceType.NOPIECE
                    and to_square.color == Side.BLACK):
                valid_move = True

            # if not direct capture, destination should be empty
            elif (self.board[to_row][to_file].piece == PieceType.NOPIECE):
                # allow two spaces if at starting point
                if (from_row == 1 and to_row == 3 and from_file == to_file
                        and self.board[2][from_file].piece
                            == PieceType.NOPIECE):
                    valid_move = True
                    is_pawn_move_two = True

                # allow en passant
                elif (from_row == black_pawn_row-2
                        and to_row == black_pawn_row-1
                        and file_diff == 1):
                    passant_target: BoardPiece = self.board[to_row-1][to_file]
                    if (passant_target.color == Side.BLACK
                            and passant_target.piece == PieceType.PAWN
                            and passant_target.last_move == self.move_num-1
                            and passant_target.pawn_move_two):
                        # remove other pawn
                        passant_target.remove()
                        valid_move = True

                # allow moving one space forward
                elif to_row == from_row+1 and from_file == to_file:
                    valid_move = True

        elif move_piece.piece == PieceType.PAWN and self.turn == Side.BLACK:
            # Black pawn
            # allow capture
            if (to_row == from_row-1
                    and file_diff == 1
                    and to_square.piece != PieceType.NOPIECE
                    and to_square.color == Side.WHITE):
                valid_move = True

            # if not direct capture, destination should be empty
            elif (self.board[to_row][to_file].piece == PieceType.NOPIECE):
                # allow two spaces if at starting point
                if (from_row == black_pawn_row
                        and to_row == black_pawn_row-2
                        and from_file == to_file
                        and self.board[black_pawn_row-1][from_file].piece
                            == PieceType.NOPIECE):
                    valid_move = True
                    is_pawn_move_two = True

                # allow en passant
                elif from_row == 3 and to_row == 2 and file_diff == 1:
                    passant_target: BoardPiece = self.board[to_row+1][to_file]
                    if (passant_target.color == Side.WHITE
                            and passant_target.piece == PieceType.PAWN
                            and passant_target.last_move == self.move_num
                            and passant_target.pawn_move_two):
                        # remove other pawn
                        passant_target.remove()
                        valid_move = True

                # allow moving one space forward
                elif to_row == from_row-1 and from_file == to_file:
                    valid_move = True

        elif move_piece.piece == PieceType.KNIGHT:
            # only need to check that destination is an L shaped jump
            if ((row_diff == 1 and file_diff == 2)
                    or (row_diff == 2 and file_diff == 1)):
                valid_move = True

        elif move_piece.piece == PieceType.BISHOP:
            # check destination is diagonal
            if row_diff != file_diff:
                raise ChessMoveError("Invalid move!")
            
            # check no other pieces in between
            row_step = 1 if to_row > from_row else -1
            file_step = 1 if to_file > from_file else -1
            next_row = from_row
            next_file = from_file
            for i in range(1,row_diff):
                next_row += row_step
                next_file += file_step
                if self.board[next_row][next_file].piece != PieceType.NOPIECE:
                    raise ChessMoveError("Invalid move!")
            
            valid_move = True

        elif move_piece.piece == PieceType.ROOK:
            # check destination is orthogonal
            if row_diff == 0:
                # check no other pieces in between
                for next_file in range(from_file+1, to_file):
                    if (self.board[from_row][next_file].piece
                            != PieceType.NOPIECE):
                        raise ChessMoveError("Invalid move!") 
            elif file_diff == 0:
                # check no other pieces in between
                for next_row in range(from_row+1, to_row):
                    if (self.board[from_file][next_row].piece
                            != PieceType.NOPIECE):
                        raise ChessMoveError("Invalid move!") 
            else:
                raise ChessMoveError("Invalid move!")
            valid_move = True

        elif move_piece.piece == PieceType.QUEEN:
            # check destination is orthogonal or diagonal
            row_step = 0
            file_step = 0
            num_steps = 0

            if row_diff == 0:
                num_steps = file_diff
                file_step = 1 if to_file > from_file else -1
            elif file_diff == 0:
                num_steps = row_diff
                row_step = 1 if to_row > from_row else -1
            elif row_diff == file_diff:
                num_steps = row_diff
                file_step = 1 if to_file > from_file else -1
                row_step = 1 if to_row > from_row else -1
            else:
                raise ChessMoveError("Invalid move!")

            # check no other pieces in between
            next_row = from_row
            next_file = from_file
            for i in range(1,num_steps):
                next_row += row_step
                next_file += file_step
                if self.board[next_row][next_file].piece != PieceType.NOPIECE:
                    raise ChessMoveError("Invalid move!")
            valid_move = True

        elif move_piece.piece == PieceType.KING:
            # check destination is only one square away in any direction
            if row_diff <= 1 and file_diff <= 1:
                valid_move = True

        if valid_move:
            BoardPiece.replace(
                self.board[from_row][from_file],
                self.board[to_row][to_file],
                self.move_num,
                is_pawn_move_two
            )
            return
        else:
            raise ChessMoveError("Invalid move!")
    
    def is_check():
        pass

    def is_checkmate():
        pass

    def is_stalemate():
        pass
    
    def run(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            self.print_board()
            print("")
            self.input_move()