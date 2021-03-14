import discord
from discord.ext import commands
import os
import traceback
import asyncio
import psycopg2

conn = psycopg2.connect(os.environ['DATABASE_URL'])
with conn.cursor() as cur:
    cur.excute('SELECT Prefix FROM BotDetail;')
    row = cur.fetchall()
    print(row)
    prefix = str(row.prefix)

bot = commands.Bot(command_prefix=prefix)
token = os.environ['DiscordBotToken']


InExtensions = [
    'reaction_roles'
]

loop = asyncio.new_event_loop()

async def run():
    bot = GenkaiMainClass()
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        await bot.logout()


class GenkaiMainClass(commands.bot):

    def __init__(self):
        super.__init__(command_prefix=commands.when_mentioned_or(prefix), loop=loop)
    
    async def on_ready(self):
        for extension in InExtensions:
            try:
                self.load_extension(f'cogs.{extension}')
            except commands.ExtensionAlreadyLoaded:
                self.reload_extension(f'cogs.{extension}')
        await self.change_presence(activity=discord.Game(name=f'{prefix}help'))
    
    async def on_command_error(self, ctx, error1):
        if isinstance(error1, (commands.CommandNotFound, commands.CommandInvokeError)):
            return


if __name__ == '__main__':
    try:
        main_task = loop.create_task(run())
        loop.run_until_complete(main_task)
        loop.close()

    except Exception as error:
        print('Error:\n  ' + traceback.format_exc())