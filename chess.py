import copy
from email.errors import NonPrintableDefect
import enum
import os
from tkinter import PIESLICE
from typing import List, Optional

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
    def __init__(self, piece: PieceType, color: Side, row, file):
        self.piece = piece
        self.color = color
        self.last_move = 0  # for special moves like castling
        self.pawn_move_two = False  # was last move a pawn moving two squares
        self.row = row
        self.file = file
        self.next: BoardPiece = None  # for linked list of pieces of the same side
        self.prev: BoardPiece = None

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
        self.piece_list: dict[Side, Optional[BoardPiece]] = {
            Side.WHITE: None, Side.BLACK: None}
        self.kings = {Side.WHITE: None, Side.BLACK: None}

        for i in range(Chess.BOARD_SIZE):
            self.board[i] = [None,] * Chess.BOARD_SIZE
            for j in range(Chess.BOARD_SIZE):
                self.board[i][j] = BoardPiece(PieceType.NOPIECE,
                                              Side.NEUTRAL,
                                              i, j)
            self.squares[i] = [' ',] * Chess.BOARD_SIZE
            self.squares[i][(i % 2):Chess.BOARD_SIZE:2] = (
                ['#',] * ((Chess.BOARD_SIZE + i%2) // 2))

        # Set up default chessboard
        for piece_position in Chess.SETUP:
            (row, file, piece, color) = piece_position
            try:
                self.add_piece(piece, color, row, file, 0)
                if piece == PieceType.KING:
                    self.kings[color] = self.board[row][file]
            except IndexError:
                # Do nothing if out of range
                pass
        
        assert(self.kings[Side.WHITE] is not None)
        assert(self.kings[Side.BLACK] is not None)

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
        passant_target: Optional[BoardPiece] = None
        kingside_castling_rook: Optional[BoardPiece] = None
        queenside_castling_rook: Optional[BoardPiece] = None
        other_side = Side.WHITE if self.turn == Side.BLACK else Side.BLACK
        general_error_msg = "Invalid move!"

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
                    passant_target = self.board[to_row-1][to_file]
                    if (passant_target.color == Side.BLACK
                            and passant_target.piece == PieceType.PAWN
                            and passant_target.last_move == self.move_num-1
                            and passant_target.pawn_move_two):
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
                    passant_target = self.board[to_row+1][to_file]
                    if (passant_target.color == Side.WHITE
                            and passant_target.piece == PieceType.PAWN
                            and passant_target.last_move == self.move_num
                            and passant_target.pawn_move_two):
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
                raise ChessMoveError(general_error_msg)
            
            # check no other pieces in between
            row_step = 1 if to_row > from_row else -1
            file_step = 1 if to_file > from_file else -1
            next_row = from_row
            next_file = from_file
            for i in range(1,row_diff):
                next_row += row_step
                next_file += file_step
                if self.board[next_row][next_file].piece != PieceType.NOPIECE:
                    raise ChessMoveError(general_error_msg)
            
            valid_move = True

        elif move_piece.piece == PieceType.ROOK:
            # check destination is orthogonal
            if row_diff == 0:
                # check no other pieces in between
                file_step = 1 if to_file > from_file else -1
                for next_file in range(from_file+file_step,
                                       to_file, file_step):
                    if (self.board[from_row][next_file].piece
                            != PieceType.NOPIECE):
                        raise ChessMoveError(general_error_msg)
            elif file_diff == 0:
                # check no other pieces in between
                row_step = 1 if to_row > from_row else -1
                for next_row in range(from_row+row_step, to_row, row_step):
                    if (self.board[next_row][from_file].piece
                            != PieceType.NOPIECE):
                        raise ChessMoveError(general_error_msg)
            else:
                raise ChessMoveError(general_error_msg)
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
                raise ChessMoveError(general_error_msg)

            # check no other pieces in between
            next_row = from_row
            next_file = from_file
            for i in range(1,num_steps):
                next_row += row_step
                next_file += file_step
                if self.board[next_row][next_file].piece != PieceType.NOPIECE:
                    raise ChessMoveError(general_error_msg)
            valid_move = True

        elif move_piece.piece == PieceType.KING:
            # check if castling
            if move_piece.last_move == 0:
                # Kingside castling
                if to_file == from_file+2:
                    castling_rook = self.board[from_row][from_file+3]
                    if (castling_rook.piece == PieceType.ROOK
                            and castling_rook.color == self.turn
                            and castling_rook.last_move == 0
                            and self.board[from_row][from_file+1].piece
                                == PieceType.NOPIECE):
                        if self.is_square_attacked(from_row, from_file+1,
                                                   other_side):
                            raise ChessMoveError("Cannot castle through check")
                        kingside_castling_rook = castling_rook
                
                # Queenside castling
                if to_file == from_file-2:
                    castling_rook = self.board[from_row][from_file-4]
                    if (castling_rook.piece == PieceType.ROOK
                            and castling_rook.color == self.turn
                            and castling_rook.last_move == 0
                            and self.board[from_row][from_file-1].piece
                                == PieceType.NOPIECE
                            and self.board[from_row][from_file-3].piece
                                == PieceType.NOPIECE):
                        if self.is_square_attacked(from_row, from_file+1,
                                                   other_side):
                            raise ChessMoveError("Cannot castle through check")
                        queenside_castling_rook = castling_rook
                
            # check destination is only one square away in any direction
            elif row_diff > 1 or file_diff > 1:
                raise ChessMoveError(general_error_msg)

            # verify that king does not move into check
            if self.is_square_attacked(to_row, to_file, other_side):
                raise ChessMoveError("Cannot move King into check!")

            valid_move = True

        if not valid_move:
            raise ChessMoveError(general_error_msg)
        
        # save pieces before moving with shallow copies
        from_piece_copy = copy.copy(self.board[from_row][from_file])
        to_piece_copy = copy.copy(self.board[to_row][to_file])
        self.move_piece(from_row, from_file, to_row, to_file, is_pawn_move_two)

        # check that this move has not exposed king to check
        if self.is_square_attacked(self.kings[self.turn].row,
                                   self.kings[self.turn].file,
                                   other_side):
            # reset pieces to previous move and then raise error
            self.move_piece(to_row, to_file, from_row, from_file,
                            from_piece_copy.pawn_move_two)
            self.board[from_row][from_file].last_move = \
                from_piece_copy.last_move
            if to_piece_copy.piece != PieceType.NOPIECE:
                self.add_piece(to_piece_copy.piece, to_piece_copy.color,
                               to_row, to_file, to_piece_copy.last_move,
                               to_piece_copy.pawn_move_two)
            raise ChessMoveError("Cannot put own King into check")

        if passant_target is not None:
            passant_target.remove()
        if kingside_castling_rook is not None:
            self.move_piece(kingside_castling_rook.row,
                            kingside_castling_rook.file,
                            to_row, to_file-1)
        if queenside_castling_rook is not None:
            self.move_piece(queenside_castling_rook.row,
                            queenside_castling_rook.file,
                            to_row, to_file+1)

    
    def remove_piece(self, piece_row, piece_file):
        target_piece = self.board[piece_row][piece_file]
        if target_piece.piece != PieceType.NOPIECE:
            if target_piece.prev is None:  # is head of list
                self.piece_list[target_piece.color] = target_piece.next
            else:  # is not head of list
                target_piece.prev.next = target_piece.next
            if target_piece.next is not None:
                target_piece.next.prev = None
            target_piece.next = None
            target_piece.prev = None
            target_piece.piece = PieceType.NOPIECE
            target_piece.color = Side.NEUTRAL
            target_piece.last_move = 0
            target_piece.pawn_move_two = False
    
    def add_piece(self, piece: PieceType, color: Side,
                  row, file, last_move=None, pawn_move_two=False):
        # adding new piece to the board
        self.remove_piece(row, file)
        new_square = self.board[row][file]
        new_square.piece = piece
        new_square.color = color
        if last_move is None:
            new_square.last_move = self.move_num
        else:
            new_square.last_move = last_move
        new_square.pawn_move_two = pawn_move_two
        # add to head of piece list
        old_head = self.piece_list[color]
        if old_head is not None:
            old_head.prev = new_square
            new_square.next = old_head
        new_square.prev = None
        self.piece_list[color] = new_square
    
    def move_piece(self, from_row, from_file, to_row, to_file,
                   is_pawn_move_two=False):
        self.remove_piece(to_row, to_file)
        from_piece = self.board[from_row][from_file]
        self.add_piece(from_piece.piece, from_piece.color, to_row, to_file,
                       pawn_move_two = is_pawn_move_two)
        if from_piece.piece == PieceType.KING:
            self.kings[from_piece.color] = self.board[to_row][to_file]
        self.remove_piece(from_row, from_file)

    def is_square_attacked(self, target_row, target_file, by_side: Side):
        pieces = self.piece_list[by_side]

        while pieces is not None:
            row_diff = abs(target_row - pieces.row)
            file_diff = abs(target_file - pieces.file)

            if pieces.piece == PieceType.PAWN:
                # check if attacked by pawns
                if file_diff == 1:
                    if by_side == Side.BLACK and pieces.row-1 == target_row:
                        return True
                    elif by_side == Side.WHITE and pieces.row+1 == target_row:
                        return True

            if pieces.piece == PieceType.KING:
                # check if attacked by another King
                if file_diff <= 1 and row_diff <= 1:
                    return True

            if pieces.piece in [PieceType.QUEEN, PieceType.ROOK]:
                # check if attacked orthogonally by Rook or Queen
                if row_diff == 0:
                    # check no other pieces in between
                    blocked = False
                    file_step = 1 if target_file > pieces.file else -1
                    for next_file in range(pieces.file+file_step,
                                           target_file, file_step):
                        if (self.board[target_row][next_file].piece
                                != PieceType.NOPIECE):
                            blocked = True
                            break
                    if not blocked:
                        return True
                elif file_diff == 0:
                    blocked = False
                    row_step = 1 if target_row > pieces.row else -1
                    for next_row in range(pieces.row+row_step,
                                          target_row, row_step):
                        if (self.board[next_row][target_file].piece
                                != PieceType.NOPIECE):
                            blocked = True
                            break
                    if not blocked:
                        return True

            if pieces.piece in [PieceType.QUEEN, PieceType.BISHOP]:
                # check if attacked diagonally by Bishop or Queen
                if row_diff == file_diff:
                    # check no other pieces in between
                    row_step = 1 if target_row > pieces.row else -1
                    file_step = 1 if target_file > pieces.file else -1
                    next_row = pieces.row
                    next_file = pieces.file
                    blocked = False
                    for i in range(1, row_diff):
                        next_row += row_step
                        next_file += file_step
                        if (self.board[next_row][next_file].piece
                                != PieceType.NOPIECE):
                            blocked = True
                            break
                    if not blocked:
                        return True

            # check if attacked by Knights
            if pieces.piece == PieceType.KNIGHT:
                if ((row_diff == 1 and file_diff == 2)
                        or (row_diff == 2 and file_diff == 1)):
                    return True

            # Go to next piece
            pieces = pieces.next
        
        return False

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