import discord
from discord.ext import commands



class clear(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=['clear'], description='Cancella messaggi nella chat', invoke_without_command=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def cancella(self, ctx, amount: int):
        if amount < 201:
            await ctx.channel.purge(limit=amount)
        else:
            embed = discord.Embed(title=":warning: | Stai cercando di cancellare piu di 200 messaggi!", colour=discord.Colour.red())
            await ctx.send(embed=embed)


    @cancella.command(aliases=['until', 'fino'])
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def until_subcommand(self, ctx, ID: int):
        try:
            await ctx.channel.fetch_message(ID)
            async for message in ctx.channel.history(limit=200):
                if message.id == ID:
                    await message.add_reaction("⚠")
                    await message.clear_reaction('⚠')
                    break
                else:
                    await message.delete()
        except:
            await ctx.send('Message non trovato')

    @cancella.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title="", colour=discord.Colour.red())
            embed.add_field(name="Quanti messaggi devo cancellare?", value='```Esempio:\ncancella 10\ncancella fino ID_DEL_MESSAGGIO```', inline=False)
            await ctx.send(embed=embed)
        elif isinstance(error, commands.errors.BadArgument):
            embed = discord.Embed(title="", colour=discord.Colour.red())
            embed.add_field(name="Quanti messaggi devo cancellare?", value='```Esempio:\ncancella 10\ncancella fino ID_DEL_MESSAGGIO```', inline=False)
            await ctx.send(embed=embed)

    @until_subcommand.error
    async def until_subcommand(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title="", colour=discord.Colour.red())
            embed.add_field(name="Quanti messaggi devo cancellare?", value='```Esempio:\ncancella 10\ncancella fino ID_DEL_MESSAGGIO```', inline=False)
            await ctx.send(embed=embed)
        elif isinstance(error, commands.errors.BadArgument):
            embed = discord.Embed(title="", colour=discord.Colour.red())
            embed.add_field(name="Quanti messaggi devo cancellare?", value='```Esempio:\ncancella 10\ncancella fino ID_DEL_MESSAGGIO```', inline=False)
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(clear(bot))