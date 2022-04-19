from dis import disco
import discord
import random
import time
import json
from discord.ext import tasks, commands

from amazons import game, agents

class AmazonsCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg : discord.Message):
        if msg.author.id != 963682692732428330:
            return

        try:
            player, turn, game_data = msg.content.split('|')
        except Exception as e:
            return

        if int(player) != self.bot.user.id:
            return

        game_data = json.loads(game_data)

        game_id = game_data['id']

        if game_data['playerWhite'] == self.bot.user.id:
            own = game.Piece.white_amazon
        else:
            own = game.Piece.black_amazon

        board_data = game_data['board']

        board = []
        for row in board_data:
            board.append([])
            for column in row:
                piece = game.Piece(column)
                board[-1].append(piece)

        ai = agents.Terror("Terror", distance_eval=lambda d: 1/min(d, 3), unreachable_value=-0.2)
        move, value = ai.select_move(board, own)
        
        (start_y, start_x), (move_y, move_x), (shoot_y, shoot_x) = move

        move_string = f'<@963682692732428330>|play|{game_id}|{start_x},{start_y}|{move_x},{move_y}|{shoot_x},{shoot_y}'
        await msg.channel.send(f'Board State Evaluation: {value}')
        await msg.channel.send(move_string)
        

    @commands.command()
    async def amazon_start(self, ctx, opponent : str):
        await ctx.send(f'<@963682692732428330> | start | {opponent}')


def setup(bot: commands.Bot):
    bot.add_cog(AmazonsCog(bot))