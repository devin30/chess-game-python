import enum
import os
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

    def remove(self):
        self.piece = PieceType.NOPIECE
        self.color = Side.NEUTRAL
        self.last_move = -1

    def replace(from_piece: "BoardPiece", to_piece: "BoardPiece", move_num):
        to_piece.piece = from_piece.piece
        to_piece.color = from_piece.color
        to_piece.last_move = move_num
        from_piece.piece = PieceType.NOPIECE
        from_piece.color = Side.NEUTRAL
        from_piece.last_move = -1
    


class ChessInputError(Exception):
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
                break
            except ChessInputError as e:
                print(e)
                continue

        while True:
            try:
                print("Enter position to move to")
                dest_pos = input(">>> ")
                (dest_row, dest_file) = Chess.parse_position(dest_pos)
                break
            except ChessInputError as e:
                print(e)
                continue
        
        # Move piece
        BoardPiece.replace(
            self.board[piece_row][piece_file],
            self.board[dest_row][dest_file],
            self.move_num
        )
        
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