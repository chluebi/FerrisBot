import math

from amazons.game import *
from amazons.agents import *

# Terror("Terror", distance_eval=lambda d: 1/min(d, 3), unreachable_value=-0.2)

game = Game()
ai1 = Terror("Terror", distance_eval=lambda d: 1/min(d, 3), unreachable_value=-0.2)
ai2 = Terror("Terror", distance_eval=lambda d: 1/min(d, 3), unreachable_value=0)


#game.board = [[Piece.nothing for j in range(20)] for i in range(20)]
#game.board[0][0] = Piece.black_amazon
#game.board[1][1] = Piece.white_amazon
while not game.finished:
    if game.current_player == Player.white:
        move, value = ai1.select_move(game.board, Piece.white_amazon)
        game.move(move)
    else:
        move, value = ai2.select_move(game.board, Piece.black_amazon)
        game.move(move)
    print(game.format(move))
    print(move, value)
    print('AI1:', ai1.evaluate(game.board, Piece.white_amazon))
    print('AI2:', ai2.evaluate(game.board, Piece.black_amazon))
    print('-----')