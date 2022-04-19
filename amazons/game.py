from copy import deepcopy
from math import copysign
from enum import Enum
from random import Random


class Player(Enum):
    white = 0
    black = 1


class Piece(Enum):
    nothing = 0
    white_amazon = 1
    black_amazon = 2
    arrow = 3


class MoveState(Enum):
    rejected = 0
    accepted = 1
    game_over = 2


class Agent:

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"Agent {self.name}"

    def select_move(self, board, own):
        # makes a list of all the pieces we can move
        potential_pieces = []
        for x in range(len(board)):
            for y in range(len(board[0])):
                if board[y][x] == own and _can_move(board, x, y):
                    potential_pieces.append([x, y])

        # finds the movements a random piece can make
        rand = Random()
        x, y = move_from = rand.choice(potential_pieces)
        potential_direction = _find_possible_move(board, x, y)
        x, y = move_to = rand.choice(potential_direction)

        # copies the board to find a random arrow place
        tmp_board = deepcopy(board)
        tmp_board[y][x] = Piece.nothing
        tmp_board[y][x] = own

        potential_arrow = _find_possible_move(tmp_board, x, y)
        arrow_to = rand.choice(potential_arrow)

        # moves the piece
        return (move_from, move_to, arrow_to)


class Game:

    def __init__(self):
        self.board = self._setup()
        self.finished = False
        self.current_player = Player.white

    def _setup(self):
        board = [[Piece.nothing for _ in range(10)] for _ in range(10)]
        board[0][3] = board[0][6] = board[3][0] = board[3][9] = Piece.black_amazon
        board[9][3] = board[9][6] = board[6][0] = board[6][9] = Piece.white_amazon
        return board

    def is_over(self, player: Player):
        lf = Piece.white_amazon if player == Player.white else Piece.black_amazon

        for y, row in enumerate(self.board):
            for x, piece in enumerate(row):
                if piece == lf and self._can_move(x, y):
                    return False
        return True

    def _find_possible_move(self, x, y, board=None):
        """Finds the possible moves allowed from that coordinate"""
        if board is None:
            board = self.board
        possible_movement = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if y+i < 0 or x+j < 0:
                    continue
                if y+i >= len(board) or x+j >= len(board):
                    continue
                if board[y+i][x+j] == Piece.nothing:
                    possible_movement.append([x+j, y+i])
        return possible_movement

    def _can_move(self, x, y):
        # checks if a piece can move
        return len(self._find_possible_move(x, y)) > 0

    def json_format(self):
        board = [[x.value for x in row] for row in self.board]
        return str(
            {
                "id": self.id,
                "board": board,
                "playerWhite": self.player_white,
                "playerBlack": self.player_black
            }
        )

    def format(self, move):

        (start_y, start_x), (move_y, move_x), (arrow_y, arrow_x) = move
        chessboard = [
            ["🟨" if (i+j) % 2 == 0 else "🟧" for j in range(len(self.board))] for i in range(len(self.board[0]))]
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                if self.board[i][j] == Piece.black_amazon:
                    chessboard[i][j] = "⬛"
                if self.board[i][j] == Piece.white_amazon:
                    chessboard[i][j] = "⬜"
                if self.board[i][j] == Piece.arrow:
                    chessboard[i][j] = "🟦"

                if (i, j) == (start_y, start_x):
                    if chessboard[i][j] == '🟨':
                        chessboard[i][j] = '🟡'
                    elif chessboard[i][j] == '🟧':
                        chessboard[i][j] = '🟠'

                if (i, j) == (move_y, move_x):
                    if chessboard[i][j] == '⬛':
                        chessboard[i][j] = '⚫'
                    elif chessboard[i][j] == '⬜':
                        chessboard[i][j] = '⚪'

                if (i, j) == (arrow_y, arrow_x):
                    chessboard[i][j] = '🔵'

        return "\n".join(["".join(row) for row in chessboard])

    def move(self, move):
        """Handles the movement of a piece and its arrow"""
        move_from, move_to, arrow_to = move

        if self.finished:
            return MoveState.rejected, "This game is already over"

        y1, x1 = move_from
        y2, x2 = move_to
        y3, x3 = arrow_to

        if self.board[y1][x1] not in [Piece.white_amazon, Piece.black_amazon]:
            return MoveState.rejected, "Not a piece to move"

        piece = self.board[y1][x1]

        # check if moving the amazon is valid
        valid, reason = _is_valid_move(self.board, move_from, move_to)
        if not valid:
            return MoveState.rejected, "Can't move the amazon that way"
        # moves the amazon (without saving yet)
        tmp_board = deepcopy(self.board)
        tmp_board[y1][x1] = Piece.nothing
        tmp_board[y2][x2] = piece

        # check if shooting the arrow is valid
        valid, reason = _is_valid_move(tmp_board, move_to, arrow_to)
        if not valid:
            return MoveState.rejected, "Can't shoot the arrow like that"

        # move the piece on the board and shoot the arrow (with saving)
        self.board[y1][x1] = Piece.nothing
        self.board[y2][x2] = piece
        self.board[y3][x3] = Piece.arrow

        if self.current_player == Player.white:
            self.current_player = Player.black
        else:
            self.current_player = Player.white

        # check if the game is over
        if self.is_over(self.current_player):
            self.finished = True
            return MoveState.game_over, "Game Over"

        return MoveState.accepted, "Move accepted"

def _is_valid_move(board, move_from, move_to):
    """Checks if a move is valid with the current board configuration
    """
    y1, x1 = move_from
    y2, x2 = move_to
    if x1 == x2 and y1 == y2:
        return False, "x and y are the same"

    if abs(y2 - y1) == abs(x2 - x1) or x2-x1 == 0 or y2-y1 == 0:
        signx = int(copysign(1, x2-x1))
        if x2-x1 == 0:
            signx = 0
        signy = int(copysign(1, y2-y1))
        if y2-y1 == 0:
            signy = 0
        for i in range(1, max(abs(y2-y1), abs(x2-x1))+1):
            if board[y1+i*signy][x1+i*signx] != Piece.nothing:
                return False, f"diag: something in the way on {(x1+i*signx, y1+i*signy)}"
        return True, "correct"

    return False, "Invalid movement (not diagonal or straight)"

def _find_possible_move(board, x, y):
        """Finds the possible moves allowed from that coordinate"""
        possible_movement = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                k = 1
                while True:
                    if y+i*k < 0 or x+j*k < 0:
                        break
                    if y+i*k >= len(board) or x+j*k >= len(board):
                        break
                    if board[y+i*k][x+j*k] == Piece.nothing:
                        possible_movement.append((y+i*k, x+j*k))
                    else:
                        break
                    k += 1
        return possible_movement

def _can_move(board, x, y):
    # checks if a piece can move
    return len(_find_possible_move(board, x, y)) > 0

def queen_move(board, move):
    move_from, move_to = move
    y1, x1 = move_from
    y2, x2 = move_to

    if board[y1][x1] not in [Piece.white_amazon, Piece.black_amazon]:
        print('not a piece')
        return None

    piece = board[y1][x1]

    # check if moving the amazon is valid
    valid, reason = _is_valid_move(board, move_from, move_to)
    if not valid:
        print('not a valid move')
        return None

    board[y1][x1] = Piece.nothing
    board[y2][x2] = piece

    return board


def arrow_move(board, move):

    move_from, move_to = move
    y1, x1 = move_from
    y2, x2 = move_to

    # check if shooting the arrow is valid
    valid, reason = _is_valid_move(board, move_from, move_to)
    if not valid:
        return None

    board[y2][x2] = Piece.arrow

    return board


def move(board, move):
    """Handles the movement of a piece and its arrow"""

    move_from, move_to, arrow_to = move

    tmp_board = deepcopy(board)
    tmp_board = queen_move(board, (move_from, move_to))
    if tmp_board is None:
        return None

    tmp_board = arrow_move(board, (move_to, arrow_to))
    
    return tmp_board