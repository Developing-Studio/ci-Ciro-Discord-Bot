import asyncio
import datetime
import locale
import discord
import pytz
from discord.ext import commands
from Ciro import get_prefix_tx


class ricordami(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.rik = 0
        locale.setlocale(locale.LC_ALL, 'it_IT')

    @commands.bot_has_permissions(embed_links=True)
    @commands.command(aliasas=['promemoria'], description='Ti ricorda di fare qualcosa dopo un lasso di tempo')
    async def ricordami(self, ctx, tra, tempo: int, tipo_di_tempo, *, what=None):
        if tra == 'tra':
            emb = discord.Embed(title=f":clock: | Promemoria",
                                description=f"Creato il {datetime.datetime.now(pytz.timezone('Europe/Rome')).strftime('%d %B %Y alle %H:%M')}:\n\n{what}\n\n[Messaggio D'origine]({ctx.message.jump_url})",
                                colour=discord.Colour.dark_teal())
            await ctx.send(f"Ok, te lo ricorderò nel canale {ctx.channel.mention}!")
            self.bot.rik += 1
            if tipo_di_tempo in ("seconds", "second", "sec", "secs", "s", "secondi", "secondo"):

                await asyncio.sleep(int(tempo))
                self.bot.rik -= 1
                return await ctx.send(content=ctx.author.mention, embed=emb)

            elif tipo_di_tempo in ("minutes", "min", "minuti", "minuto"):

                for a in range(int(tempo)):
                    await asyncio.sleep(60)
                self.bot.rik -= 1
                return await ctx.send(content=ctx.author.mention, embed=emb)

            elif tipo_di_tempo in ("hours", "hour", "h", "ore", "ora"):

                for a in range(int(tempo)):
                    await asyncio.sleep(3600)
                self.bot.rik -= 1
                return await ctx.send(content=ctx.author.mention, embed=emb)
        else:
            await ctx.send(f'Utilizzo:\n{get_prefix_tx(self.bot, message=ctx.message)}ricordami tra X ore promemoria\n{get_prefix_tx(self.bot, message=ctx.message)}ricordami tra X minuti promemoria\n{get_prefix_tx(self.bot, message=ctx.message)}ricordami tra X secondi promemoria')

    @ricordami.error
    async def ricordami_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title="", colour=discord.Colour.red())
            embed.add_field(name="Utilizzo", value=f'{get_prefix_tx(self.bot, message=ctx.message)}ricordami tra X ore promemoria\n{get_prefix_tx(self.bot, message=ctx.message)}ricordami tra X minuti promemoria\n{get_prefix_tx(self.bot, message=ctx.message)}ricordami tra X secondi promemoria', inline=False)
            await ctx.send(embed=embed)
        elif isinstance(error, commands.errors.BadArgument):
            embed = discord.Embed(title="", colour=discord.Colour.red())
            embed.add_field(name="Utilizzo", value=f'{get_prefix_tx(self.bot, message=ctx.message)}ricordami tra X ore promemoria\n{get_prefix_tx(self.bot, message=ctx.message)}ricordami tra X minuti promemoria\n{get_prefix_tx(self.bot, message=ctx.message)}ricordami tra X secondi promemoria', inline=False)
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ricordami(bot))