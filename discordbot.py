import discord
from discord.ext import commands
import os
import traceback
import asyncio
import psycopg2

def getConnection():
    return psycopg2.connect(os.environ['DATABASE_URL'])

with getConnection() as conn:
    print(conn)
    with conn.cursor() as cur:
        print(cur)
        cur.execute('SELECT Prefix FROM BotDetail;')
        row = cur.fetchone()
        print(row)
        prefix = str(row[0])
        print(prefix)

intents = discord.Intents.default()
intents.members = True
print(intents)
token = os.environ['DiscordBotToken']


InExtensions = [
    'about',
    'reaction_roles'
]

loop = asyncio.new_event_loop()

async def run():
    bot = GenkaiMainClass()
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        print('logout...')
        await bot.logout()


class GenkaiMainClass(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or(prefix), loop=loop, intents=intents)
    
    async def on_ready(self):
        for extension in InExtensions:
            try:
                self.load_extension(f'cogs.{extension}')
            except commands.ExtensionAlreadyLoaded:
                self.reload_extension(f'cogs.{extension}')
        await self.change_presence(activity=discord.Game(name=f'{prefix}help'))
    
    #async def on_command_error(self, ctx, error1):
    #    if isinstance(error1, (commands.CommandNotFound, commands.CommandInvokeError)):
    #        embed = discord.Embed()
    #        embed.add_field(name='エラー(このメッセージは自動的に削除されます)', value=repr(error1))
    #        a = await ctx.send(embed=embed)
    #        await asyncio.sleep(10)
    #        await a.delete()
    #        return


if __name__ == '__main__':
    try:
        main_task = loop.create_task(run())
        loop.run_until_complete(main_task)
        loop.close()

    except Exception as error:
        print('Error:\n  ' + traceback.format_exc())