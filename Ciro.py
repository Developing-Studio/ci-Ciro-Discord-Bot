import json
import time
import discord
from discord.ext import commands
import os
import sys

#  #  #  REQUIREMENTS  #  #  #
if not os.path.isdir('./data'):
    os.mkdir('data')
    if not os.path.isfile('./data/prefixes.json'):
        with open("data/prefixes.json", "w") as l:
            l.write('{}')
            l.close()

if not os.path.isfile('./crash.0'):
    print('Missing "crash.0" file, where your bot-token is stored')
    sys.exit(1)

#  #  #  REQUIREMENTS  #  #  #


#  #  #  CHECK  #  #  #


def owner(ctx):
    return ctx.message.author.id == 323058900771536898


def get_prefix(bot, message):
    with open("data/prefixes.json", "r") as f:
        prefixes = json.load(f)
    try:
        return prefixes[str(message.guild.id)]
    except KeyError:
        prefixes[str(message.guild.id)] = 'c-'

        with open('data/prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)

        return prefixes[str(message.guild.id)]


#  #  #  CHECK  #  #  #


bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True)
bot.remove_command('help')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')


@bot.event
async def on_ready():
    print("Pronto come", bot.user)
    await bot.change_presence(activity=discord.Game(name="c-help"))

    # a = commands.clean_content(use_nicknames=True)
    # message = await a.convert(ctx, message)


#  #  #  CUSTOM PREFIX  #  #  #


@bot.event
async def on_guild_join(guild):
    with open('data/prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = 'c-'

    with open('data/prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

    ch = bot.get_channel(715151965713072180)
    emb = discord.Embed(description=f"<a:YAAY:715156619842814023>\n{bot.user.mention} si è unito al server **{guild.name}**\n proprieatario del server :  **{guild.owner}**\n Membri nel server : **{guild.member_count}**", colour=discord.Colour.green())
    emb.set_footer(text=f"sono online in {len(bot.guilds)} server", icon_url=bot.user.avatar_url)
    emb.set_thumbnail(url=guild.icon_url)
    if guild.banner:
        emb.set_image(url=guild.banner_url)
    await ch.send(embed=emb)


@bot.event
async def on_guild_remove(guild):
    try:
        with open('data/prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefixes.pop(str(guild.id))

        with open('data/prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)
    except Exception as e:
        await bot.get_channel(714813858530721862).send(str(e) + 'server' + str(guild.id))

    ch = bot.get_channel(715151965713072180)
    emb = discord.Embed(description=f"<a:SAAD:715156620388335647>\n{bot.user.mention} ha lasciato il server **{guild.name}**\n proprieatario del server :  **{guild.owner}**\n Membri nel server : **{guild.member_count}**", colour=discord.Colour.red())
    emb.set_footer(text=f"sono online in {len(bot.guilds)} server", icon_url=bot.user.avatar_url)
    emb.set_thumbnail(url=guild.icon_url)
    if guild.banner:
        emb.set_image(url=guild.banner_url)
    await ch.send(embed=emb)

#  #  #  COMANDI STANDARD  #  #  #


@bot.command(description=f'Mostra la latenza di <@714798417746067547>')
async def ping(ctx):
    start = time.perf_counter()

    raw = discord.Embed(colour=discord.Colour.green(), description=f"```...```", title="Ping!")
    msg = await ctx.send(embed=raw)

    end = time.perf_counter()
    duration = (end - start) * 1000

    pong = round(bot.latency * 1000)

    emb = discord.Embed(colour=discord.Colour.green(), description=f"""
    ```prolog\nLatency  :: {pong} ms\nResponse :: {duration:.2f} ms\n```""", timestamp=ctx.message.created_at,
                        title="Pong!")
    await msg.edit(embed=emb, content=None)


@bot.command(aliases=['invite'], description=f'Mostra la latenza di <@714798417746067547>')
async def invito(ctx):
    await ctx.send(f'Invita ciro nel tuo server <https://discord.com/oauth2/authorize?client_id=714798417746067547&permissions=0&scope=bot>')


@bot.group(description='Mostra questo messaggio', invoke_without_command=True)
async def help(ctx):
    try:
        embed = discord.Embed(title=f"Lista comandi", colour=discord.Colour(0xFCFCFC), timestamp=ctx.message.created_at)
        embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
        embed.set_footer(text="https://discord.gg/3jACDJT")
        for x in bot.commands:
            if not x.hidden:
                if not x.description:
                    embed.add_field(name=f"{bot.command_prefix(bot, message=ctx.message)}{x.name}", value=f'#',
                                    inline=False)
                else:
                    embed.add_field(name=f"{bot.command_prefix(bot, message=ctx.message)}{x.name}",
                                    value=f'{x.description}', inline=False)
        await ctx.send(embed=embed)
    except:
        y = '```fix\nATTENZIONE:\n per il funzionamento corretto dei comandi mi serve il permesso "Incorporare Link"!```\n'
        for x in bot.commands:
            if not x.hidden:
                if not x.description:
                    y += f"{bot.command_prefix(bot, message=ctx.message)}{x.name} - #\n"
                else:
                    y += f"{bot.command_prefix(bot, message=ctx.message)}{x.name} - {x.description}\n"
        await ctx.send(y)


@bot.group(description=f'Cambia il prefisso di  <@714798417746067547> in questo server')
@commands.has_permissions(manage_guild=True)
async def prefisso(ctx, prefisso):
    with open('data/prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefisso

    with open('data/prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

    await ctx.send(f'Ho cambiato il prefisso in questo server in `{prefisso}`')


#  #  #  OWNER  #  #  #


@bot.command(description='Carica l’estensione', hidden=True)
@commands.check(owner)
async def load(ctx, extension):
    try:
        bot.load_extension(f'cogs.{extension}')

        await ctx.message.add_reaction("✅")
    except Exception as e:
        await ctx.message.add_reaction("❌")
        await bot.get_channel(714813858530721862).send(str(e))


@bot.command(description='Disabilita l’estensione', hidden=True)
@commands.check(owner)
async def unload(ctx, extension):
    try:
        bot.unload_extension(f'cogs.{extension}')

        await ctx.message.add_reaction("✅")
    except Exception as e:
        await ctx.message.add_reaction("❌")
        await bot.get_channel(714813858530721862).send(str(e))


@bot.command(description='Ricarica l’estensione', hidden=True)
@commands.check(owner)
async def reload(ctx, extension):
    try:
        bot.unload_extension(f'cogs.{extension}')
        bot.load_extension(f'cogs.{extension}')

        await ctx.message.add_reaction("✅")
    except Exception as e:
        await ctx.message.add_reaction("❌")
        await bot.get_channel(714813858530721862).send(str(e))


@bot.command(description='Mostra i cogs', hidden=True)
@commands.check(owner)
@commands.bot_has_permissions(embed_links=True)
async def cogs(ctx):
    cogsloaded = ''
    cogsunloaded = ''
    embed = discord.Embed(title="Index", colour=discord.Colour(0xFCFCFC), timestamp=ctx.message.created_at)
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)

    for x in bot.cogs:
        cogsloaded += f'{x}\n'

    embed.add_field(name=f"Loaded Cogs:", value=f'```\n{cogsloaded}```', inline=False)

    for x in os.listdir('./cogs'):
        if x.endswith('.py'):
            if x[:-3] not in cogsloaded:
                cogsunloaded += f'{x[:-3]}\n'

    embed.add_field(name=f"Unloaded Cogs:", value=f'```\n{cogsunloaded}```', inline=False)
    await ctx.send(embed=embed)


@help.command(name='me')
@commands.check(owner)
async def me_subcommand(ctx):
    embed = discord.Embed(title="Owner Panel", colour=discord.Colour(0xFCFCFC), timestamp=ctx.message.created_at)

    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
    embed.set_footer(text="https://discord.gg/3jACDJT")

    for x in bot.commands:
        if x.hidden:
            if not x.description:
                embed.add_field(name=f"{bot.command_prefix}{x.name}", value=f'404', inline=False)
            else:
                embed.add_field(name=f"{bot.command_prefix}{x.name}", value=f'```{x.description}```', inline=False)

    msg = await ctx.send(embed=embed)
    await msg.delete(delay=60)


@prefisso.command(name='reset')
@commands.check(owner)
async def reset_subcommand(ctx, id_gilda: int):
    with open("data/prefixes.json", "r") as f:
        prefixes = json.load(f)
    try:
        prefixes[str(id_gilda)] = 'c-'

        with open('data/prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)

        await ctx.send(f'Ho resettato correttamente il prefisso in `c-` nella gilda `{id_gilda}`')
    except KeyError:
        await ctx.send(f'La gilda {id_gilda} non è in lista, il prefisso default è `c-`')


@bot.command(description='Spegne il bot', hidden=True)
@commands.check(owner)
async def arresta(ctx):
    await ctx.send("Arresto in corso...")
    await bot.logout()


@bot.command(description='Riavvia il bot', hidden=True)
@commands.check(owner)
async def riavvia(ctx):
    await ctx.send("Riavvio in corso...")
    await bot.logout()
    os.system("python3 Ciro.py")


bot.run(open("crash.0", "r").readline().strip())