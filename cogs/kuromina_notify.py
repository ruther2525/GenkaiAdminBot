import os
from discord.ext import commands
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
                self.KuroMinaNotifyList.append({'id': int(user_id)})
                await ctx.send('たぶんできた')
                print(repr(self.KuroMinaNotifyList))

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        print(repr(member))
        if after.channel is not None and (member.id == 227375367990542338 or member.id == 553991444172374027):
            kuromina_tmp = 0
            for a in after.channel.members:
                if a.id == 227375367990542338 or a.id == 553991444172374027:
                    kuromina_tmp += 1
            
            if kuromina_tmp > 1:
                for row in self.KuroMinaNotifyList:
                    user = self.bot.get_user(row.id)
                    await user.send('【くろみな通知】くろみなが限界創作村の __' + str(after.channel.name) + '__ に参加しました')

def setup(bot):
    bot.add_cog(kuromina_notify(bot))
