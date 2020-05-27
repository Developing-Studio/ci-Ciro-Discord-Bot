import asyncio
import discord
from discord.ext import commands



class ricordami(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.bot_has_permissions(manage_messages=True)
    @commands.command(aliasas=['promemoria'], description='Ti ricorda di fare qualcosa dopo un lasso di tempo')
    async def ricordami(self, ctx, tra, tempo: int, tipo_di_tempo, *, what=None):
        if tra == 'tra':
            emb = discord.Embed(title=f":clock: | Promemoria",
                                description=f"Creato il {ctx.message.created_at.strftime('%d %B %Y [%I:%M %p] CEST')}:\n\n{what}\n\n[Messaggio D'origine]({ctx.message.jump_url})",
                                colour=discord.Colour.dark_teal())

            await ctx.send(f"Ok, te lo ricorderò nel canale {ctx.channel.mention}!")

            if tipo_di_tempo in ("seconds", "second", "sec", "secs", "s", "secondi", "secondo"):

                await asyncio.sleep(int(tempo))

                return await ctx.send(content=ctx.author.mention, embed=emb)

            elif tipo_di_tempo in ("minutes", "min", "minuti", "minuto"):

                for a in range(int(tempo)):
                    await asyncio.sleep(60)

                return await ctx.send(content=ctx.author.mention, embed=emb)

            elif tipo_di_tempo in ("hours", "hour", "h", "ore", "ora"):

                for a in range(int(tempo)):
                    await asyncio.sleep(3600)

                return await ctx.send(content=ctx.author.mention, embed=emb)
        else:
            await ctx.send(f'Utilizzo:\n{self.bot.command_prefix(self.bot, message=ctx.message)}ricordami tra X ore promemoria\n{self.bot.command_prefix(self.bot, message=ctx.message)}ricordami tra X minuti promemoria\n{self.bot.command_prefix(self.bot, message=ctx.message)}ricordami tra X secondi promemoria')

    @ricordami.error
    async def ricordami_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title="", colour=discord.Colour.red())
            embed.add_field(name="Utilizzo", value=f'{self.bot.command_prefix(self.bot, message=ctx.message)}ricordami tra X ore promemoria\n{self.bot.command_prefix(self.bot, message=ctx.message)}ricordami tra X minuti promemoria\n{self.bot.command_prefix(self.bot, message=ctx.message)}ricordami tra X secondi promemoria', inline=False)
            await ctx.send(embed=embed)
        elif isinstance(error, commands.errors.BadArgument):
            embed = discord.Embed(title="", colour=discord.Colour.red())
            embed.add_field(name="Utilizzo", value=f'{self.bot.command_prefix(self.bot, message=ctx.message)}ricordami tra X ore promemoria\n{self.bot.command_prefix(self.bot, message=ctx.message)}ricordami tra X minuti promemoria\n{self.bot.command_prefix(self.bot, message=ctx.message)}ricordami tra X secondi promemoria', inline=False)
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ricordami(bot))