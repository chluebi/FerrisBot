# library imports
import os
import logging
import traceback
import discord
import asyncio
from discord.ext import commands

# local imports
import util

discord_config = util.parse_config('discord')

# determining intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=discord_config['prefix'], intents=intents)

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

    await util.send_embed(ctx, util.error_embed(ctx, f'```{error}```'))

    logging.error(error_message)

extensions = {}

@commands.check(util.is_owner)
@bot.group(name='extension')
async def extension(ctx : commands.Context):
    if ctx.invoked_subcommand is None:
        embed = util.standard_embed(ctx, 'Shows loaded extensions', title='Loaded Extensions')
        embed.add_field(name='Loaded', value='⏰' + '\n'.join(key for key, value in extensions.items() if value))
        embed.add_field(name='Not Loaded', value='😴' + '\n'.join(key for key, value in extensions.items() if not value))
        await ctx.send(embed=embed)

@extension.command(name='load')
async def load_extension(ctx : commands.Context, name : str):
    if name not in extensions:
        await util.send_embed(ctx, util.error_embed(ctx, f'Extension ``{name}`` not found.'))
        return
    if extensions[name]:
        await util.send_embed(ctx, util.error_embed(ctx, f'Extension ``{name}`` already loaded.'))
        return
    extensions[name] = True
    import_path = 'cogs.' + name
    bot.load_extension(import_path)
    await util.send_embed(ctx, util.success_embed(ctx, f'Extension ``{name}`` loaded.'))

@extension.command(name='unload')
async def unload_extension(ctx : commands.Context, name : str):
    if name not in extensions:
        await util.send_embed(ctx, util.error_embed(ctx, f'Extension ``{name}`` not found.'))
    if not extensions[name]:
        await util.send_embed(ctx, util.error_embed(ctx, f'Extension ``{name}`` already not loaded.'))
        return
    extensions[name] = False
    import_path = 'cogs.' + name
    bot.unload_extension(import_path)
    await util.send_embed(ctx, util.success_embed(ctx, f'Extension ``{name}`` unloaded.'))

    
# iterate over all files in the "cogs folder"
for file in os.listdir('cogs'):
    if file == "__pycache__":
        continue

    file_name = file.split('.')[0]
    extensions[file_name] = True
    import_path = 'cogs.' + file_name
    asyncio.run(bot.load_extension(import_path))


bot.run(discord_config['token'])