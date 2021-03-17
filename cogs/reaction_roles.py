import os
import discord
from discord.ext import commands
import asyncio
import psycopg2
import asyncpg

client = discord.Client()

class reaction_roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print(bot)

        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM R_R_List;')
            rows = cur.fetchall()
            print(rows)

            self.r_r_listen_list = []
            for now_row in rows:
                print(now_row)
                a = {}
                if now_row[1] == 1:
                    a['is_true'] = True
                else:
                    a['is_true'] = False
                a['message_id'] = now_row[0]
                a['server_id'] = now_row[2]
                a['emoji'] = now_row[3]
                a['role'] = int(now_row[4])
                self.r_r_listen_list.append(a)
            
            if self.r_r_listen_list is not None:
                print(self.r_r_listen_list)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def rrdel(self, ctx, operation, message_id, delete_role: discord.Role):
        if operation == 'set':
            embed = discord.Embed(title='このメッセージにリアクションロールで使用したい絵文字を１分以内にリアクションしてください。サーバー固有絵文字はやばいかも。', color=discord.Colour.green())
            reaction_message = await ctx.send(embed=embed)
            
            def check(reaction, user):
                print('Check function runned')
                print('  Reaction: ' + repr(reaction))
                print('  User: ' + repr(user))
                print('  Return: ' + repr(user == ctx.author and reaction.message.id == reaction_message.id))
                return user == ctx.author and reaction.message.id == reaction_message.id

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
                print('a')
            except asyncio.TimeoutError:
                await reaction_message.delete()
                await ctx.send('タイムアウトしました')
                pass
            else:
                try:
                    server_id = ctx.message.guild.id

                    to_listen_msg = await ctx.fetch_message(message_id)
                    print(to_listen_msg)
                    if to_listen_msg is not None:
                        await to_listen_msg.add_reaction(reaction.emoji)
                    

                    embed = discord.Embed(title="設定内容")
                    embed.add_field(name="**メッセージid**", value=message_id)
                    embed.add_field(name="**リアクションの絵文字**", value=str(reaction.emoji))
                    embed.add_field(name="**リアクションにより削除するロール**", value=str(delete_role))
                    
                    print(delete_role)
                    await ctx.send(embed=embed)

                    async_conn = await asyncpg.connect(os.environ['DATABASE_URL'])
                    sql = f"INSERT INTO R_R_List(message_id, is_true, server_id, emoji, role) VALUES ('{message_id}', 1, '{server_id}', '{str(reaction.emoji)}', '{delete_role.id}');"
                    print(sql)
                    await async_conn.execute(sql)
                    await async_conn.close()
                    
                    a = {}
                    a['message_id'] = message_id
                    a['server_id'] = server_id
                    a['emoji'] = str(reaction.emoji)
                    a['role'] = int(delete_role.id)
                    self.r_r_listen_list.append(a)
                    
                    await ctx.send('該当メッセージにリアクションを設定し、データベースに保存しました。これでできるはずです。たぶん。')

                except discord.Forbidden:
                    await ctx.send('エラーが発生しました。権限を確認してください')

    @rrdel.error
    async def rrdel_error(self, error, ctx):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(title='エラー', description='管理権限が必要です')
            error_msg = await ctx.send(embed=embed)
            await asyncio.sleep(10)
            await error_msg.delete()
        return
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        print('on_raw_reaction_add fired')
        print('  self: ' + repr(self))
        print('  payload: ' + repr(payload))
        for unko in self.r_r_listen_list:
            print('unko: ' + repr(unko))
            print('\n' + repr(payload.message_id == unko['message_id']))
            print('\n' + repr(str(payload.emoji) == str(unko['emoji'])))
            if payload.message_id == unko['message_id'] and str(payload.emoji) == str(unko['emoji']):
                guild = self.bot.get_guild(int(payload.guild_id))
                print(guild)
                if guild is not None:

                    delete_role = guild.get_role(int(unko['role']))
                    print(delete_role)
                    if delete_role is not None:
                        await payload.member.remove_roles(delete_role)
                        return

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(member)
        for role in self.r_r_listen_list:
            print(role)
            if member.guild.id == int(role['server_id']):
                getrole = member.guild.get_role(int(role['role']))
                if getrole is not None:
                    await member.add_roles(getrole)


def setup(bot):
    bot.add_cog(reaction_roles(bot))