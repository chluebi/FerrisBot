from amazons.game import *
from amazons.agents import *

game = Game()
ai = Terror("Terror")
random_ai = Random("Random")

#game.board = [[Piece.nothing for j in range(20)] for i in range(20)]
#game.board[0][0] = Piece.black_amazon
#game.board[1][1] = Piece.white_amazon
while not game.finished:
    if game.current_player == Player.white:
        move = ai.select_move(game.board, Piece.white_amazon)
        game.move(move)
    else:
        move = ai.select_move(game.board, Piece.black_amazon)
        game.move(move)
    print(game.format())
    print(ai.evaluate(game.board, Piece.white_amazon))
    print('-----')