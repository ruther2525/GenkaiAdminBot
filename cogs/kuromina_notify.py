import os
from discord.ext import commands
import discord
import psycopg2
import asyncpg
from discord.ext.commands import bot

class kuromina_notify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM KuroMinaNotify;')
            rows = cur.fetchall()

            self.KuroMinaNotifyList = rows
            print(rows)
    
    @commands.command()
    async def kuromina(self, ctx, operation, user_id: int):
        if ctx.author.id == 722072905604923393:
            if operation == 'add':

                async_conn = await asyncpg.connect(os.environ['DATABASE_URL'])
                sql = f"INSERT INTO KuroMinaNotify(id) VALUES ({user_id});"
                await async_conn.execute(sql)
                self.KuroMinaNotifyList.append(tuple([user_id]))
                user = self.bot.get_user(user_id)
                embed = discord.Embed()
                embed.add_field(name='できた', value='{} さん'.format(user.mention))
                await ctx.send(embed=embed)
                print(repr(self.KuroMinaNotifyList))
    
    @commands.command()
    async def krmn_list(self, ctx):
        embed = discord.Embed(title='くろみな通知 | 通知一覧', color=discord.Colour.dark_orange())
        print(self.KuroMinaNotifyList)
        for a in self.KuroMinaNotifyList:
            print(a)
            user = self.bot.get_user(int(a[0]))
            if user is not None:
                embed.add_field(name=str(user.name), value=str(user.id))
        await ctx.send(embed=embed)

    @commands.command()
    async def dm_totu(self, ctx, message: str):
        for a in self.KuroMinaNotifyList:
            user = self.bot.get_user(int(a[0]))
            if user is not None:
                user.send(message)
        
        await ctx.reply('できたよ')

    """
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel is not None and (member.id == 227375367990542338 or member.id == 553991444172374027):
            kuromina_tmp = 0
            for a in after.channel.members:
                if a.id == 227375367990542338 or a.id == 553991444172374027:
                    kuromina_tmp += 1
            
            if kuromina_tmp > 1:
                for row in self.KuroMinaNotifyList:
                    user = self.bot.get_user(int(row[0]))
                    try:
                        await user.send('【くろみな通知】くろみなが限界創作村の __*' + str(after.channel.name) + '*__ に参加しました')
                    except discord.Forbidden:
                        print('User: "' + user.name + '" is not open DM, so bot cant send DM')
        """
def setup(bot):
    bot.add_cog(kuromina_notify(bot))
