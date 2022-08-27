import math

from amazons.game import *
from amazons.agents import *

# Terror("Terror", distance_eval=lambda d: 1/min(d, 3), unreachable_value=-0.2)
# DeepTerror("DeepTerror Alpha", lambda d: 1/min(d, 3), -0.2, 10, 10, 7, 2)
# DeepTerror("DeepTerror Wide", lambda d: 1/min(d, 3), -0.2, 7, 7, 20, 2)
# DeepTerror("DeepTerror Shiv", lambda d: 1/min(d, 3), -0.2, 7, 7, 4, 2)
# DeepTerror("DeepTerror Knife", lambda d: 1/min(d, 3), -0.2, 5, 5, 6, 2)
# FreeTerror("FreeTerror", lambda d: 1/min(d, 3), -0.2, 2, lambda p, r: min(5, int(math.sqrt(p))), 700)
# FreeTerror("FreeTerror Shiv", lambda d: 1/min(d, 3), -0.2, 2, lambda p, r: min(max(1, 4-r), int(math.sqrt(p))), 240)

game = Game()
ai1 = DeepTerror("DeepTerror Knife", lambda d: 1/min(d, 3), -0.2, 5, 5, 6, 2)
ai2 = DeepTerror("DeepTerror Knife", lambda d: 1/min(d, 3), -0.2, 5, 5, 6, 6)



#game.board = [[Piece.nothing for j in range(7)] for i in range(7)]
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