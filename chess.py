import enum

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

    def __init__(self):
        self.board = [[],] * Chess.BOARD_SIZE
        self.squares = [[],] * Chess.BOARD_SIZE  # square colours
        for i in range(Chess.BOARD_SIZE):
            self.board[i] = [(PieceType.NOPIECE, Side.NEUTRAL),] * Chess.BOARD_SIZE
            self.squares[i] = [' ',] * Chess.BOARD_SIZE
            self.squares[i][(i % 2):Chess.BOARD_SIZE:2] = (
                ['#',] * ((Chess.BOARD_SIZE + i%2) // 2))

        # Set up default chessboard
        for piece_position in Chess.SETUP:
            (row, file, piece, color) = piece_position
            try:
                self.board[row][file] = (piece, color)
            except IndexError:
                # Do nothing if out of range
                pass

    def print_board(self):
        print("")

        # top of board
        for i in range(Chess.BOARD_SIZE):
            print("__", end="")
        print("_")
        
        for row in range(Chess.BOARD_SIZE-1,-1,-1):
            for file, piece in enumerate(self.board[row]):
                print("|", end="")
                if piece[0] == PieceType.NOPIECE:
                    print(self.squares[row][file], end="")
                elif piece[1] == Side.WHITE:
                    print(Chess.WHITE_PIECES[piece[0]], end="")
                elif piece[1] == Side.BLACK:
                    print(Chess.BLACK_PIECES[piece[0]], end="")
                else:
                    raise Exception("Piece not belonging to either side")
            print("|")
