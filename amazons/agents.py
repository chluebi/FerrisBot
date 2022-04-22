from collections import deque
from copy import deepcopy
import random
import math
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

        if len(moves) < 1:
            return super().select_move(board, own)
        
        return moves[0]


class DeepTerror(Terror):

    def __init__(self, name, distance_eval, unreachable_value, move_cutoff, arrow_cutoff, deep_divider, responsiveness):
        super().__init__(name, distance_eval, unreachable_value)
        self.move_cutoff = move_cutoff
        self.arrow_cutoff = arrow_cutoff
        self.deep_divider = deep_divider
        self.responsiveness = responsiveness

    def select_move(self, board, own):
        move, evaluation = self.search_move(board, own, 1, 0, 0)[0]
        return move, evaluation

    def search_move(self, board, own, divider, r, max_recursion):
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
            for move_y, move_x in neigh:
                tmp_board = deepcopy(board)
                tmp_board = queen_move(tmp_board, ((y, x), (move_y, move_x)))
                if tmp_board is None:
                    continue

                queen_moves.append((
                    ((y, x), (move_y, move_x)),
                    self.evaluate(tmp_board, own)
                ))

        queen_moves.sort(key=lambda x: x[1], reverse=True)
        queen_moves = queen_moves[:self.move_cutoff//divider + 1]

        moves = []
        for ((y, x), (move_y, move_x)), evaluation in queen_moves:
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
                    self.evaluate(tmp_arrow_board, own),
                    tmp_arrow_board
                    ))

        moves.sort(key=lambda x: x[1], reverse=True)
        moves = moves[:(len(queen_moves)*self.arrow_cutoff)//divider + 1]
        if len(moves) < 1:
            return []
        if len(moves) < 2:
            return [(moves[0][0], moves[0][1])]

        if divider == 1:
            moves = tqdm(moves)

        def other_color(piece):
            if piece == Piece.white_amazon:
                return Piece.black_amazon
            else:
                return Piece.white_amazon

        deep_moves = []
        for ((y, x), (move_y, move_x), (arrow_y, arrow_x)), evaluation, board in moves:
            follow_ups = self.search_move(board, other_color(own), divider*self.deep_divider, r+1, max_recursion)
            if len(follow_ups) < 1:
                return [(((y, x), (move_y, move_x), (arrow_y, arrow_x)), 100000)]

            enemy_evaluation = follow_ups[0][1]
            deep_moves.append((
                ((y, x), (move_y, move_x), (arrow_y, arrow_x)),
                evaluation - self.responsiveness * enemy_evaluation
            ))

        deep_moves.sort(key=lambda x: x[1], reverse=True)
        return deep_moves


class FreeTerror(Terror):

    def __init__(self, name, distance_eval, unreachable_value, responsiveness, r_cutoff, max_sample):
        super().__init__(name, distance_eval, unreachable_value)
        self.responsiveness = responsiveness
        self.r_cutoff = r_cutoff
        self.max_sample = max_sample

    def select_move(self, board, own):
        pieces = []
        for y in range(len(board)):
            for x in range(len(board[0])):
                if board[y][x] == own:
                    pieces.append((y, x))

        possibility_space = 0
        for p in pieces:
            neigh = self.neighbors(board, (y, x))
            l = len(neigh)
            possibility_space += l*l

        max_recursion = 0
        cutoff = self.r_cutoff(possibility_space, max_recursion)
        x = cutoff*cutoff+1
        print('x0', x)
        while x < self.max_sample and max_recursion < 5:
            max_recursion += 1
            cutoff = self.r_cutoff(possibility_space, max_recursion)
            x = (x)*(cutoff*cutoff+1)
            print('x', x)

        max_recursion -= 1

        print('max recursion', max_recursion)
        
        self.iterations = 0
        move, evaluation = self.search_move(board, own, possibility_space, 0, max_recursion)[0]
        return move, evaluation

    def search_move(self, board, own, initial_possibility_space, r, max_recursion):
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
            for move_y, move_x in neigh:
                tmp_board = deepcopy(board)
                tmp_board = queen_move(tmp_board, ((y, x), (move_y, move_x)))
                if tmp_board is None:
                    continue

                queen_moves.append((
                    ((y, x), (move_y, move_x)),
                    self.evaluate(tmp_board, own)
                ))

        cutoff = self.r_cutoff(initial_possibility_space, r)
        queen_moves.sort(key=lambda x: x[1], reverse=True)
        queen_moves = queen_moves[:cutoff + 1]

        if r == 0:
            queen_moves = tqdm(queen_moves)

        moves = []
        for ((y, x), (move_y, move_x)), evaluation in queen_moves:
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
                    self.evaluate(tmp_arrow_board, own),
                    tmp_arrow_board
                    ))

        moves.sort(key=lambda x: x[1], reverse=True)
        moves = moves[:cutoff*cutoff + 1]
        if len(moves) < 1:
            return []
        if len(moves) < 2:
            return [(moves[0][0], moves[0][1])]

        if r + 1 > max_recursion or self.iterations > self.max_sample:
            return [(moves[0][0], moves[0][1])]

        if r == 0:
            moves = tqdm(moves)

        def other_color(piece):
            if piece == Piece.white_amazon:
                return Piece.black_amazon
            else:
                return Piece.white_amazon

        deep_moves = []
        for ((y, x), (move_y, move_x), (arrow_y, arrow_x)), evaluation, board in moves:
            follow_ups = self.search_move(board, other_color(own), initial_possibility_space, r+1, max_recursion)
            if len(follow_ups) < 1:
                return [(((y, x), (move_y, move_x), (arrow_y, arrow_x)), 100000)]

            enemy_evaluation = follow_ups[0][1]
            deep_moves.append((
                ((y, x), (move_y, move_x), (arrow_y, arrow_x)),
                evaluation - self.responsiveness * enemy_evaluation
            ))

        deep_moves.sort(key=lambda x: x[1], reverse=True)
        return deep_moves
