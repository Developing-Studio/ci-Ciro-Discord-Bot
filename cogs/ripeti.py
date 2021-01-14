import aiohttp
from io import BytesIO
import discord
from discord.ext import commands


class ripeti(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    null = ''

    @commands.bot_has_permissions(attach_files=True, embed_links=True)
    @commands.command(aliases=['repeat'], description='Ripete il tuo messaggio')
    async def ripeti(self, ctx, *, arg=null):
        message = ctx.message
        if message.attachments:
            arg = await commands.clean_content(use_nicknames=True).convert(ctx, arg)
            filename = message.attachments[0].filename
            attachment = message.attachments[0].url
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment) as resp:
                    image_bytes = await resp.read()
            file = discord.File(BytesIO(image_bytes), filename=filename)
            await ctx.send(arg, file=file)
        else:
            if arg == '' and not message.attachments:
                embed = discord.Embed(title="", colour=discord.Colour.red())
                embed.add_field(name="Qual'è il messaggio da ripetere?",
                                value='```Esempio:\nripeti pizza```', inline=False)
                await ctx.send(embed=embed)
            else:
                arg = await commands.clean_content(use_nicknames=True).convert(ctx, arg)
                await ctx.send(arg)

    @commands.bot_has_permissions(manage_messages=True, attach_files=True, embed_links=True)
    @commands.has_permissions(manage_messages=True, mention_everyone=True)
    @commands.command(aliases=['repeatdel'], description='Ripete e cancella il tuo messaggio')
    async def ripeticanc(self, ctx, *, arg=null):
        message = ctx.message
        if message.attachments:
            filename = message.attachments[0].filename
            attachment = message.attachments[0].url
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment) as resp:
                    image_bytes = await resp.read()
            file = discord.File(BytesIO(image_bytes), filename=filename)
            await ctx.message.delete()
            await ctx.send(arg, file=file)
        else:
            if arg == '' and not message.attachments:
                embed = discord.Embed(title="", colour=discord.Colour.red())
                embed.add_field(name="Qual'è il messaggio da ripetere?",
                                value='```Esempio:\nripeticanc pizza```', inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.message.delete()
                await ctx.send(arg)

    @commands.bot_has_permissions(manage_messages=True, administrator=True, attach_files=True, embed_links=True)
    @commands.has_permissions(manage_messages=True, mention_everyone=True)
    @commands.command(aliases=['send2'], description='Invia il tuo messaggio in un canale')
    async def inoltra(self, ctx, target: discord.TextChannel, *, arg=null):
        message = ctx.message
        if message.attachments:
            filename = message.attachments[0].filename
            attachment = message.attachments[0].url
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment) as resp:
                    image_bytes = await resp.read()
            file = discord.File(BytesIO(image_bytes), filename=filename)
            await ctx.message.delete()
            await target.send(arg, file=file)
        else:
            if arg == '' and not message.attachments:
                embed = discord.Embed(title="", colour=discord.Colour.red())
                embed.add_field(name="Qual'è il messaggio da inoltrare?",
                                value='```Esempio:\ninoltra #canale pizza```', inline=False)
                await ctx.send(embed=embed)
            else:
                await target.send(arg)

    @inoltra.error
    async def inoltra_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandInvokeError):
            message = await ctx.send(f'{error}')
            await message.delete(delay=5)
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            embed = discord.Embed(title="", colour=discord.Colour.red())
            embed.add_field(name="Errore",
                            value=f"```Qual'è il canale di destinazione?\ninoltra #canale messaggio```", inline=False)
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ripeti(bot))
