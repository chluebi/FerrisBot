
import discord
from discord.ext import tasks, commands


class PlaceCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.placing = False

    def cog_unload(self):
        self.place_pixel.cancel()

    @tasks.loop(seconds=5.0)
    async def place_pixel(self):
        pass

    @commands.group(name='place')
    async def place(self, ctx : commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send(f'Status of placing: ``{self.placing}``')

    @place.command(name='start')
    async def start(self, ctx : commands.Context):
        self.place_pixel.start()
        await ctx.send('Started Placing.')
        self.placing = True

    @place.command(name='stop')
    async def start(self, ctx : commands.Context):
        self.place_pixel.cancel()
        await ctx.send('Stopped Placing.')
        self.placing = False

def setup(bot: commands.Bot):
    bot.add_cog(commands.Cog(bot))