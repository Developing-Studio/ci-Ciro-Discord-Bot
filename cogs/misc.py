import asyncio
import os
from datetime import datetime
import json
import time
import platform
import aiohttp
import psutil
import discord
from discord.ext import commands, tasks
from discord.ext.commands import RoleConverter
from Ciro import get_prefix_tx


class misc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.stats.start()
        self.launchtime = datetime.now()

    @commands.command(aliases=['help'], description='Mostra questo messaggio')
    async def aiuto(self, ctx, *, comando: str = None):
        try:
            if not comando:
                embed = discord.Embed(title=f"Lista comandi", colour=discord.Colour(0xFCFCFC))
                for x in os.listdir('./cogs'):
                    if x.endswith('.py'):
                        if x != 'owner.py' and x != 'test.py':
                            value = ''
                            try:
                                for c in self.bot.get_cog(x[:-3]).get_commands():
                                    if not c.hidden:
                                        value += f'  {c.name}\n'
                                        try:
                                            if self.bot.get_command(c.name).commands:
                                                for a in self.bot.get_command(c.name).commands:
                                                    value += f'  {c.name} {a.name}\n'
                                        except:
                                            pass
                                if value != '':
                                    embed.add_field(name=f"Modulo : {x[:-3]}", value=value, inline=False)
                            except:
                                pass
                embed.add_field(name=f" ឵឵ ", value='Per maggiori informazioni scrivi:\nhelp `nome comando`',
                                inline=False)
                await ctx.send(embed=embed)
            else:
                raw_comando = self.bot.get_command(comando)
                if not raw_comando:
                    await ctx.send('Questo comando non esiste!')
                    return
                if str(raw_comando.aliases) != '[]':
                    raw_comando.aliases = str(raw_comando.aliases).replace("[", "").replace("]", "").replace("'",
                                                                                                             "`").replace(
                        ",", " -")
                    await ctx.send(f"Alias : {raw_comando.aliases}\nDescrizione : {raw_comando.description}")
                else:
                    await ctx.send(f"Descrizione : {raw_comando.description}")
        except:
            if not comando:
                generale = '```arm\n'
                for x in os.listdir('./cogs'):
                    if x.endswith('.py'):
                        if x != 'owner.py' and x != 'test.py':
                            value = ''
                            try:
                                for c in self.bot.get_cog(x[:-3]).get_commands():
                                    if not c.hidden:
                                        value += f'  {c.name}\n'
                                        try:
                                            if self.bot.get_command(c.name).commands:
                                                for a in self.bot.get_command(c.name).commands:
                                                    value += f'  {c.name} {a.name}\n'
                                        except:
                                            pass
                                generale += f"Modulo : {x[:-3]}\n{value}"
                            except:
                                pass
                generale += f'```\n\nPer maggiori informazioni scrivi:\nhelp `nome comando`\n\nSTAI VISUALIZZANDO IL FORMATO SENZA EMBED!\nUSA IL COMANDO `{get_prefix_tx(self.bot, message=ctx.message)}setup` per maggiori info'
                await ctx.send(generale)
            else:
                raw_comando = self.bot.get_command(comando)
                if not raw_comando:
                    await ctx.send('Questo comando non esiste!')
                    return
                if str(raw_comando.aliases) != '[]':
                    await ctx.send(f"Alias : {raw_comando.aliases}\nDescrizione : {raw_comando.description}")
                else:
                    await ctx.send(f"Descrizione : {raw_comando.description}")

    @commands.bot_has_permissions(embed_links=True)
    @commands.command(description=f'Mostra la latenza di <@714798417746067547>')
    async def ping(self, ctx):
        start = time.perf_counter()

        raw = discord.Embed(colour=discord.Colour.green(), description=f"```...```", title="Ping!")
        msg = await ctx.send(embed=raw)

        end = time.perf_counter()
        duration = (end - start) * 1000

        pong = round(self.bot.latency * 1000)

        emb = discord.Embed(colour=discord.Colour.green(), description=f"""
        ```prolog\nLatenza  :: {pong} ms\nRisposta :: {duration:.2f} ms\n```""", timestamp=ctx.message.created_at,
                            title="Pong!")
        await msg.edit(embed=emb, content=None)

    @commands.command(aliases=["stats", "uptime", "about", 'invite', 'invita'],
                      description='Mostra le statistiche del bot e link utili')
    @commands.bot_has_permissions(embed_links=True)
    async def online(self, ctx):
        with open("data/stats.json", "r") as f:
            l = json.load(f)

        emb = discord.Embed(
            description=f"**Sviluppatore: `IT | Kewai#9029`\nLibreria: `discord.py {discord.__version__}"
                        f"`\nVersione Python: `{platform.python_version()}`"
                        f"\nMemoria: `{psutil.virtual_memory()[2]}%`"
                        f"\nCPU: `{psutil.cpu_percent()}%`"
                        f'\nTemp: `{l["temp"]}°C`'
                        f'\nUptime: `{l["uptime"]}`'
                        f"\nOnline su: `{platform.system()}`"
                        f"\nSono in: `{len(self.bot.guilds)}` server"
                        f"\nUtenti: `{len(self.bot.users)}`"
                        f"\nInvitami nel tuo server: [clicca qui](https://discord.com/oauth2/authorize?client_id=714798417746067547&permissions=0&scope=bot)"
                        f"\nEntra nel server di <@714798417746067547>: [clicca qui](https://discord.gg/Ck5rBtS)**",
            colour=discord.Colour.gold())

        await ctx.send(embed=emb)

    @tasks.loop(seconds=20)
    async def stats(self):
        with open("data/stats.json", "r") as f:
            l = json.load(f)

        uptime = datetime.now() - self.launchtime
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        l["library"] = discord.__version__
        l["python"] = platform.python_version()
        l["memory"] = psutil.virtual_memory()[2]
        l["cpu"] = psutil.cpu_percent()
        try:
            l["temp"] = round(float(str(psutil.sensors_temperatures().get('cpu-thermal')[0]).split('current=')[1].split(',')[0]), 1)
        except:
            l["temp"] = 'N/A'
        l["running"] = platform.system()
        l["guilds"] = len(self.bot.guilds)
        l["users"] = len(self.bot.users)
        l["uptime"] = f"{days}d {hours}h {minutes}m {seconds}s"

        with open("data/stats.json", "w") as f:
            json.dump(l, f, indent=4)

    @commands.group(description=f'Cambia il prefisso di  <@714798417746067547> in questo server',
                    invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def prefisso(self, ctx, prefisso: str = None):
        if prefisso:
            with open('data/prefixes.json', 'r') as f:
                prefixes = json.load(f)

            prefixes[str(ctx.guild.id)] = prefisso

            with open('data/prefixes.json', 'w') as f:
                json.dump(prefixes, f, indent=4)

            await ctx.send(f'Ho cambiato il prefisso di questo server in `{prefisso}`')
        else:
            embed = discord.Embed(title="", colour=discord.Colour.red())
            embed.add_field(name="⚠ | Questo comando modifica il prefisso in questo server",
                            value='```Esempio:\nprefisso *\n```', inline=False)
            await ctx.send(embed=embed)

    @commands.command(aliases=['vote', 'voto'], description='Mostra il link per votare il bot')
    async def vota(self, ctx):
        await ctx.send('https://top.gg/bot/714798417746067547/vote')

    @commands.command(description='Invia un feedback allo sviluppatore del bot')
    async def feedback(self, ctx, *, message=None):
        if message:
            embed = discord.Embed(title="", colour=discord.Colour.blue())
            embed.add_field(name=ctx.author, value=f'```{message}```', inline=False)
            await self.bot.get_channel(715194608870752286).send(embed=embed)
            await ctx.send('feedback inviato.')
        else:
            await ctx.send(
                f'Esempio:\n{get_prefix_tx(self.bot, message=ctx.message)}feedback Aggiungi un sasso')

    @commands.command(description='Mostra se un utente è dal cellulare')
    async def mobile(self, ctx, member: discord.Member = None):
        if member:
            if member.is_on_mobile():
                await ctx.send('Sì')
            else:
                await ctx.send('No')
        else:
            if ctx.author.is_on_mobile():
                await ctx.send('Sì')
            else:
                await ctx.send('No')

    @commands.command(description='Mostra quali membri hanno quel ruolo (case-sensitive)')
    async def cerca(self, ctx, *, arg=None):
        try:
            role = await RoleConverter().convert(ctx, arg)
            paginator = commands.Paginator()
            r = discord.utils.get(ctx.guild.roles, name=f'{role}')
            res = ''
            if str(r.members) != '[]':
                res += f'Membri del ruolo "{role}" {len(r.members)}:\n'
                for a in r.members:
                    res += f"   {a}\n"
            print(len(res))
            if len(res) >= 2000:
                data = bytes(res, 'utf-8')
                async with aiohttp.ClientSession() as cs:
                    async with cs.post('https://hastebin.com/documents', data=data) as r:
                        res = await r.json()
                        key = res["key"]
                        return await ctx.send(f"https://hastebin.com/{key}")
            if res != '':
                try:
                    paginator.add_line(res)
                except:
                    res = res.split("\n")
                    for a in res:
                        paginator.add_line(a)
            for page in paginator.pages:
                await ctx.send(page)
                await asyncio.sleep(0.5)
        except:
            if arg:
                paginator = commands.Paginator()
                for roles in ctx.guild.roles:
                    if arg in roles.name:
                        if roles.name != '@everyone':
                            r = discord.utils.get(ctx.guild.roles, name=f'{roles}')
                            res = ''
                            if str(r.members) != '[]':
                                res += f'Membri del ruolo "{roles}" {len(r.members)}:\n'
                                for a in r.members:
                                    res += f"   {a}\n"
                            print(len(res))
                            if len(res) >= 2000:
                                data = bytes(res, 'utf-8')
                                async with aiohttp.ClientSession() as cs:
                                    async with cs.post('https://hastebin.com/documents', data=data) as r:
                                        res = await r.json()
                                        key = res["key"]
                                        return await ctx.send(f"https://hastebin.com/{key}")
                            if res != '':
                                try:
                                    paginator.add_line(res)
                                except:
                                    res = res.split("\n")
                                    for a in res:
                                        paginator.add_line(a)
                for page in paginator.pages:
                    await ctx.send(page)
                    await asyncio.sleep(0.5)
                if not paginator.pages:
                    await ctx.send('Non ho trovato nessun membro per quel ruolo o non ho trovato quel ruolo')
            else:
                paginator = commands.Paginator()
                for roles in ctx.guild.roles:
                    r = discord.utils.get(ctx.guild.roles, name=f'{roles}')
                    res = ''
                    if str(r.members) != '[]':
                        res += f'Membri del ruolo "{roles}" {len(r.members)}:\n'
                        for a in r.members:
                            res += f"   {a}\n"
                    print(len(res))
                    if len(res) >= 2000:
                        data = bytes(res, 'utf-8')
                        async with aiohttp.ClientSession() as cs:
                            async with cs.post('https://hastebin.com/documents', data=data) as r:
                                res = await r.json()
                                key = res["key"]
                                return await ctx.send(f"https://hastebin.com/{key}")
                    if res != '':
                        try:
                            paginator.add_line(res)
                        except:
                            res = res.split("\n")
                            for a in res:
                                paginator.add_line(a)
                for page in paginator.pages:
                    await ctx.send(page)
                    await asyncio.sleep(0.5)


def setup(bot):
    bot.add_cog(misc(bot))
