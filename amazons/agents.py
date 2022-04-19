from collections import deque
from copy import deepcopy
import random
from tqdm import tqdm

from amazons.game import *


class Random(Agent):
    pass


class Terror(Agent):

    def __init__(self, name, distance_eval, unreachable_value):
        super().__init__(name)
        self.distance_eval = distance_eval
        self.unreachable_value = unreachable_value

    def neighbors(self, board, pos):
        y, x = pos
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

    def evaluate(self, board, own):
        pieces = {}
        pieces[Piece.white_amazon] = []
        pieces[Piece.black_amazon] = []

        for y in range(len(board)):
            for x in range(len(board[0])):
                if board[y][x] in [Piece.white_amazon, Piece.black_amazon]:
                    pieces[board[y][x]].append((y, x))

        distances = {}
        distances[Piece.white_amazon] = [[-1 for x in range(len(board[0]))] for y in range(len(board))]
        distances[Piece.black_amazon] = [[-1 for x in range(len(board[0]))] for y in range(len(board))]

        def other_color(piece):
            if piece == Piece.white_amazon:
                return Piece.black_amazon
            else:
                return Piece.white_amazon

        for color in [Piece.white_amazon, Piece.black_amazon]:
            queue = deque()
            for piece in pieces[color]:
                y, x = piece
                queue.append((y, x, 0))
                distances[color][y][x] = 0

            while len(queue) > 0:
                y, x, dist = queue.popleft()

                for new_y, new_x in self.neighbors(board, (y, x)):
                    if distances[color][new_y][new_x] != -1:
                        continue
                    distances[color][new_y][new_x] = dist+1
                    queue.append((new_y, new_x, dist+1))

        evaluation = 0
        for y in range(len(board)):
            for x in range(len(board[0])):
                for sign, piece in [(1, Piece.white_amazon), (-1, Piece.black_amazon)]:
                    dist = distances[piece][y][x]
                    if dist == -1:
                        evaluation += sign * self.unreachable_value
                    else:
                        dist = max(1, dist)
                        value = self.distance_eval(dist)
                        evaluation += sign * value

        if own == Piece.white_amazon:
            return evaluation
        else:
            return -evaluation


    def select_move(self, board, own):
        pieces = []
        for y in range(len(board)):
            for x in range(len(board[0])):
                if board[y][x] == own:
                    pieces.append((y, x))

        queen_moves = []
        for p in pieces:
            y, x = p
            neigh = self.neighbors(board, (y, x))

            random.shuffle(neigh)
            for move_y, move_x in tqdm(neigh):
                tmp_board = deepcopy(board)
                tmp_board = queen_move(tmp_board, ((y, x), (move_y, move_x)))
                if tmp_board is None:
                    continue

                queen_moves.append((
                    ((y, x), (move_y, move_x)),
                    self.evaluate(tmp_board, own)
                ))

        queen_moves.sort(key=lambda x: x[1], reverse=True)
        queen_moves = queen_moves[:]

        moves = []
        for ((y, x), (move_y, move_x)), evaluation in tqdm(queen_moves):
            tmp_board = deepcopy(board)
            tmp_board = queen_move(tmp_board, ((y, x), (move_y, move_x)))
            neigh_arrow = self.neighbors(tmp_board, (move_y, move_x))
            random.shuffle(neigh_arrow)
            for arrow_y, arrow_x in neigh_arrow[:]:
                tmp_arrow_board = deepcopy(tmp_board)
                tmp_arrow_board = arrow_move(tmp_arrow_board, ((move_y, move_x), (arrow_y, arrow_x)))
                if tmp_arrow_board is None:
                    continue
                moves.append((
                    ((y, x), (move_y, move_x), (arrow_y, arrow_x)),
                    self.evaluate(tmp_arrow_board, own)
                    ))

        moves.sort(key=lambda x: x[1], reverse=True)
        
        return moves[0]