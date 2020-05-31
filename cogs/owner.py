import json
import os
import io
import textwrap
import traceback
from contextlib import redirect_stdout
import discord
from discord.ext import commands


def cleanup_code(content):
    """Automatically removes code blocks from the code."""
    # remove ```py\n```
    if content.startswith('```') and content.endswith('```'):
        return '\n'.join(content.split('\n')[1:-1])

    # remove `foo`
    return content.strip('` \n')


class owner(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    @commands.command(aliases=['eval'], description='SUDO', pass_context=True, hidden=True)
    @commands.is_owner()
    async def test(self, ctx, *, body: str = None):
        if body:
            if ctx.author.id == 323058900771536898:
                env = {
                    'bot': self.bot,
                    'ctx': ctx,
                    'channel': ctx.channel,
                    'author': ctx.author,
                    'guild': ctx.guild,
                    'message': ctx.message,
                    '_': self._last_result
                }

                env.update(globals())

                body = cleanup_code(body)
                stdout = io.StringIO()

                to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

                try:
                    exec(to_compile, env)
                except Exception as e:
                    return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

                func = env['func']
                try:
                    with redirect_stdout(stdout):
                        ret = await func()
                except Exception as e:
                    value = stdout.getvalue()
                    await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
                else:
                    value = stdout.getvalue()
                    try:
                        await ctx.message.add_reaction('\u2705')
                    except:
                        pass

                    if ret is None:
                        if value:
                            await ctx.send(f'```py\n{value}\n```')
                    else:
                        self._last_result = ret
                        await ctx.send(f'```py\n{value}{ret}\n```')
        else:
            await ctx.send('Cosa devo testare?')

    @commands.command(description='Carica l’estensione', hidden=True)
    @commands.is_owner()
    async def load(self, ctx,  extension):
        try:
            self.bot.load_extension(f'cogs.{extension}')

            await ctx.message.add_reaction("✅")
        except Exception as e:
            await ctx.message.add_reaction("❌")
            await self.bot.get_channel(714813858530721862).send(str(e))

    @commands.command(description='Disabilita l’estensione', hidden=True)
    @commands.is_owner()
    async def unload(self, ctx,  extension):
        try:
            self.bot.unload_extension(f'cogs.{extension}')

            await ctx.message.add_reaction("✅")
        except Exception as e:
            await ctx.message.add_reaction("❌")
            await self.bot.get_channel(714813858530721862).send(str(e))

    @commands.command(description='Ricarica l’estensione', hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, extension):
        try:
            self.bot.unload_extension(f'cogs.{extension}')
            self.bot.load_extension(f'cogs.{extension}')

            await ctx.message.add_reaction("✅")
        except Exception as e:
            await ctx.message.add_reaction("❌")
            await self.bot.get_channel(714813858530721862).send(str(e))

    @commands.command(description='Mostra i cogs', hidden=True)
    @commands.is_owner()
    @commands.bot_has_permissions(embed_links=True)
    async def cogs(self, ctx):
        cogsloaded = ''
        cogsunloaded = ''
        embed = discord.Embed(title="Index", colour=discord.Colour(0xFCFCFC), timestamp=ctx.message.created_at)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)

        for x in self.bot.cogs:
            cogsloaded += f'{x}\n'

        embed.add_field(name=f"Loaded Cogs:", value=f'```\n{cogsloaded}```', inline=False)

        for x in os.listdir('./cogs'):
            if x.endswith('.py'):
                if x[:-3] not in cogsloaded:
                    cogsunloaded += f'{x[:-3]}\n'

        embed.add_field(name=f"Unloaded Cogs:", value=f'```\n{cogsunloaded}```', inline=False)
        await ctx.send(embed=embed)

    @commands.command(description='Mostra i comandi del proprietario del bot', hidden=True)
    @commands.is_owner()
    @commands.bot_has_permissions(embed_links=True)
    async def owner(self, ctx):
        embed = discord.Embed(title="Owner Panel", colour=discord.Colour(0xFCFCFC), timestamp=ctx.message.created_at)

        embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")

        for x in self.bot.commands:
            if x.hidden:
                if not x.description:
                    embed.add_field(name=f"{self.bot.command_prefix(self.bot, message=ctx.message)}{x.name}", value=f'404',
                                    inline=False)
                else:
                    embed.add_field(name=f"{self.bot.command_prefix(self.bot, message=ctx.message)}{x.name}",
                                    value=f'```{x.description}```', inline=False)

        msg = await ctx.send(embed=embed)
        await msg.delete(delay=60)

    @commands.command(name='reset', description='Resetta il prefisso per un server', hidden=True)
    @commands.is_owner()
    @commands.bot_has_permissions(embed_links=True)
    async def reset(self, ctx, id_server: int = None):
        if id_server:
            with open("data/prefixes.json", "r") as f:
                prefixes = json.load(f)
            try:
                prefixes[str(id_server)] = 'c-'

                with open('data/prefixes.json', 'w') as f:
                    json.dump(prefixes, f, indent=4)

                await ctx.send(f'Ho resettato correttamente il prefisso in `c-` nella gilda `{id_server}`')
            except KeyError:
                await ctx.send(f'La gilda {id_server} non è in lista, il prefisso default è `c-`')
        else:
            embed = discord.Embed(title="⚠ | Manca l'id del server", colour=discord.Colour.red())
            await ctx.send(embed=embed)

    @commands.command(description='Spegne il bot', hidden=True)
    @commands.is_owner()
    async def arresta(self, ctx):
        await ctx.send("Arresto in corso...")
        await self.bot.logout()

    @commands.command(description='Riavvia il bot', hidden=True)
    @commands.is_owner()
    async def riavvia(self, ctx):
        await ctx.send("Riavvio in corso...")
        await self.bot.logout()
        os.system("python3 Ciro.py")


def setup(bot):
    bot.add_cog(owner(bot))
