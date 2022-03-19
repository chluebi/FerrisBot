import json
import asyncio
from tabnanny import check
from discord import Color, Embed
from discord.ext import commands

def parse_config(name):
	with open(f'configs/{name}.json', 'r+') as f:
		data = json.load(f)
	return data

async def is_owner(ctx):
	check_true = ctx.author.id == discord_config['owner']
	if not check_true:
		await send_embed(ctx, error_embed(ctx, 'This is an owner-only command.'))
	return check_true

def standard_embed(ctx: commands.Context, content, title='Info', color=Color.lighter_gray()):
	embed = Embed(title=title, description=content, color=color)
	embed.set_footer(text=f'Command Invoked by {str(ctx.author)}', icon_url=ctx.author.avatar_url)
	return embed

def error_embed(ctx: commands.Context, content, title='Error Occured', color=Color.red()):
	embed = Embed(title=title, description=content, color=color)
	embed.set_footer(text=f'Command Invoked by {str(ctx.author)}', icon_url=ctx.author.avatar_url)
	return embed

def success_embed(ctx: commands.Context, content, title='Success', color=Color.green()):
	embed = Embed(title=title, description=content, color=color)
	embed.set_footer(text=f'Command Invoked by {str(ctx.author)}', icon_url=ctx.author.avatar_url)
	return embed


async def send_embed(ctx: commands.Context, embed : Embed, delete=20):
	try:
		msg = await ctx.send(embed=embed)
		await asyncio.sleep(delete)
		await msg.delete()
	except Exception as e:
		await ctx.add_reaction('❌')


discord_config = parse_config('discord')