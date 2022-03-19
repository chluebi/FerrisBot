import discord
from discord.ext import tasks, commands
from PIL import Image

import util
import database as db

config = util.discord_config

class PlaceCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.placing = False

    def cog_unload(self):
        self.place_pixel.cancel()

    @tasks.loop(seconds=2.0)
    async def place_pixel(self):

        for i in range(3):
            pixel = db.PlacePixel.get_random()
            if pixel is None:
                return
            project = db.PlaceProject.get_by_name(pixel.project)
            project.placed += 1
            project.update()
            pixel.delete()

            guild = self.bot.get_guild(config['place']['guild'])
            channel = guild.get_channel(config['place']['channel'])

            await channel.send(f'.place setpixel {pixel.x} {pixel.y} {pixel.color}')

    @commands.command(name='place_status')
    async def place_status(self, ctx, subcommand=None):
        if subcommand is None:
            embed = util.standard_embed(ctx, f'Status of placing: ``{self.placing}``')
            projects = db.PlaceProject.get_all()
            for project in projects:
                embed.add_field(name=f'Project: {project.name}', value=f'Placed: {project.placed}/{project.total}')
            await util.send_embed(ctx, embed)
        elif subcommand == 'start':
            self.place_pixel.start()
            await util.send_embed(ctx, util.success_embed(ctx, f'Started Placing.'))
            self.placing = True
        elif subcommand == 'stop':
            self.place_pixel.cancel()
            await util.send_embed(ctx, util.success_embed(ctx, f'Stopped Placing.'))
            self.placing = False

    @commands.check(util.is_owner)
    @commands.command(name='place_project')
    async def place_project(self, ctx, name, x : int, y : int):
        await ctx.message.attachments[0].save('temp.png')
        file = Image.open('temp.png')
        width, height = file.size

        def rgb_to_hex(rgb):
            return '#%02x%02x%02x' % rgb

        
        pixels = []
        for i in range(width):
            for j in range(height):
                rgb = file.getpixel((i, j))
                color_string = rgb_to_hex((rgb[0], rgb[1], rgb[2]))
                pixels.append((i, j, color_string))

        project = db.PlaceProject(name, len(pixels), 0)
        project.insert()
        project = db.PlaceProject.get_by_name(name)

        for i, j, color in pixels:
            pixel = db.PlacePixel(0, project.name, x+i, y+j, color)
            pixel.insert()

        await util.send_embed(ctx, util.success_embed(ctx, f'Successfully generated project'))

def setup(bot: commands.Bot):
    bot.add_cog(PlaceCog(bot))