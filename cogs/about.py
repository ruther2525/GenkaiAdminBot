import discord
from discord.ext import commands
import asyncio


InExtensions = [
    'about',
    'reaction_roles',
    'kuromina_notify'
]

class About(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('pong')
        await ctx.send(f"`{self.bot.ws.latency * 1000:.0f}ms`")

    @commands.command()
    async def reload(self, ctx):
        if ctx.author.id == 722072905604923393:
            for ext in InExtensions:
                self.bot.reload_extension(f'cogs.{ext}')
        else:
            await ctx.send('るーさーじゃないだろ。ぼけ')
        a = await ctx.send('更新しました')
        await asyncio.sleep(10)
        await a.delete()

def setup(bot):
    bot.add_cog(About(bot))