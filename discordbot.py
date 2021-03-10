from discord.ext import commands
import os
import traceback

bot = commands.Bot(command_prefix='')
token = os.environ['DiscordBotToken']


@bot.event
async def on_command_error(ctx, error):
    orig_error = getattr(error, "original", error)
    error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())
    print(error_msg)


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


bot.run(token)
