import discord
import random
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
        self.placing = False
        self.place_pixel.cancel()

    @tasks.loop(seconds=2)
    async def place_pixel(self):
        pixel = db.PlacePixel.get_random()
        if pixel is None:
            return
        project = db.PlaceProject.get_by_name(pixel.project)
        project.placed += 1
        if project.placed >= project.total:
            project.delete()
        else:
            project.update()
        pixel.delete()

        guild = self.bot.get_guild(config['place']['guild'])
        channel = guild.get_channel(config['place']['channel'])

        await channel.send(f'.place setpixel {pixel.x} {pixel.y} {pixel.color}')


    @commands.group(name='place')
    async def place(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = util.standard_embed(ctx, f'Status of placing: ``{self.placing}``')
            projects = db.PlaceProject.get_all()
            for project in projects:
                embed.add_field(name=f'Project: {project.name}', value=f'Placed: {project.placed}/{project.total}')
            await util.send_embed(ctx, embed)

    @commands.check(util.is_owner)
    @place.group(name='start')
    async def place_start(self, ctx):
        self.place_pixel.start()
        await util.send_embed(ctx, util.success_embed(ctx, f'Started Placing.'))
        self.placing = True

    @commands.check(util.is_owner)
    @place.group(name='stop')
    async def place_stop(self, ctx):
        self.place_pixel.cancel()
        await util.send_embed(ctx, util.success_embed(ctx, f'Stopped Placing.'))
        self.placing = False

    @commands.check(util.is_owner)
    @place.group(name='project')
    async def place_project_add(self, ctx, name, x : int, y : int, order='id'):
        await ctx.message.attachments[0].save('dev/temp.png')
        file = Image.open('dev/temp.png')
        width, height = file.size

        def rgb_to_hex(rgb):
            return '#%02x%02x%02x' % rgb

        sort = orders[order]
        orders = {
            'id':lambda p: p,
            'mod': lambda p: min(p[0] % 10, p[1] % 10),
            'color': lambda p: p[2],
            'random': lambda p: random.random()
        }

        pixels = []
        for i in range(width):
            for j in range(height):
                rgb = file.getpixel((i, j))
                print(rgb)
                if rgb[3] >= 255:
                    pixels.append((i, j, rgb))

        pixels.sort(key=sort)

        project = db.PlaceProject(name, len(pixels), 0)
        project.insert()
        project = db.PlaceProject.get_by_name(name)

        for i, j, color in pixels:
            color_string = rgb_to_hex((color[0], color[1], color[2]))
            pixel = db.PlacePixel(0, project.name, x+i, y+j, color_string)
            pixel.insert()

        await util.send_embed(ctx, util.success_embed(ctx, f'Successfully generated project'))

    @commands.check(util.is_owner)
    @place.group(name='remove')
    async def place_project_add(self, ctx, name):
        project = db.PlaceProject.get_by_name(name)
        if project is None:
            await util.send_embed(ctx, util.error_embed(ctx, 'Project Not Found'))
        
        project.delete()
        await util.send_embed(ctx, util.success_embed(ctx, 'Project Successfully deleted'))

def setup(bot: commands.Bot):
    bot.add_cog(PlaceCog(bot))