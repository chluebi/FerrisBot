# library imports
import os
import logging
import traceback
import discord
from discord.ext import commands

# local imports
import util

discord_config = util.parse_config('discord')

# determining intents
intents = discord.Intents.default()
intents.members = True
# intents.presences = True

bot = commands.Bot(command_prefix=discord_config['prefix'], intents=intents)

'''
basic logging
to log anything just import logging and do
logging.error(text)
or
logging.info(text)
'''
logging.basicConfig(handlers=[logging.FileHandler('bot.log', 'a', encoding='utf-8')],
                    format='%(asctime)s - %(levelname)s - %(message)s')


@bot.event
async def on_ready():
    print('------------------')
    print(f'bot ready {bot.user.name}')
    print('------------------')

# removing help command to hide funny commands
bot.remove_command('help')


@bot.event
async def on_command_error(ctx, error):
    error_message = ''.join(traceback.format_exception(
        type(error), error, error.__traceback__))
    logging.error(error_message)

    # ignoring errors that do not need to be logged
    if (isinstance(error, commands.CommandNotFound)):
        await ctx.message.add_reaction('❌')
        return

    if (isinstance(error, commands.CheckFailure)):
        await ctx.message.add_reaction('❌')
        return

    if (isinstance(error, commands.MissingRequiredArgument)):
        await ctx.message.add_reaction('❌')
        return

    if (isinstance(error, commands.errors.UserNotFound)):
        await ctx.message.add_reaction('❌')
        return

    logging.error(error_message)


bot.run(discord_config['token'])