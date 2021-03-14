import os
import discord
from discord.ext import commands
import asyncio
import psycopg2
import asyncpg

class reaction_roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = discord.Client()

        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        with conn.cursor() as cur:
            cur.excute('SELECT * FROM R_R_List;')
            rows = cur.fetchall()
            print(rows)

            self.r_r_listen_list = []
            for now_row in rows:
                if now_row['is_true'] == 1:
                    now_row['is_true'] = True
                else:
                    now_row['is_true'] = False
                self.r_r_listen_list.append(now_row)

    @commands.command()
    async def rrdel(self, ctx, operation , message_id, delete_role):
        if operation == 'set':
            embed = discord.Embed(color=discord.Colour.green())
            embed.add_field(name='このメッセージにリアクションロールで使用したい絵文字を１分以内にリアクションしてください。')
            await ctx.send(embed=embed)
            
            def check(reaction, user):
                return user == ctx.author and reaction.message.id == ctx.message.id

            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=60.0, chech=check)
            except asyncio.TimeoutError:
                pass
            else:
                try:
                    await ctx.message.add_reaction(reaction.emoji)
                    
                    server_id = ctx.message.guild.id

                    async_conn = await asyncpg.connect(os.environ['DATABASE_URL'])
                    await async_conn.excute(f'INSERT INTO R_R_List(message_id, is_true, server_id, emoji, role) VALUES ({message_id}, 1, {server_id}, {str(reaction)}, {delete_role})')
                    await async_conn.close()
                    embed = discord.Embed(title="設定内容")
                    embed.add_field(name="**メッセージid**", value=message_id)
                    embed.add_field(name="**リアクションの絵文字**", value=str(reaction.emoji))
                    embed.add_field(name="**リアクションにより削除するロール**", value=str(delete_role))
                    
                    await ctx.send(embed=embed)
                    await ctx.send('該当メッセージにリアクションを設定し、データベースに保存しました。これでできるはずです。たぶん。')

                except discord.Forbidden:
                    await ctx.send('エラーが発生しました。権限を確認してください')
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        for unko in self.r_r_listen_list:
            if payload.message_id == unko.message_id and str(payload.emoji) == str(unko.emoji):
                guild = self.client.get_guild(payload.guild_id)
                if guild is not None:
                    a = unko.role.replace('<', '')
                    a = a.replace('@', '')
                    a = a.replace('>', '')

                    delete_role = guild.get_role(int(a))
                    if delete_role is not None:
                        await payload.member.remove_roles(delete_role)
                        return


def setup(bot):
    bot.add_cog(reaction_roles(bot))