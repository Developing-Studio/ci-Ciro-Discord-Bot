import json
import discord
from discord.ext import commands
import os
import sys
import jishaku

#  #  #  REQUIREMENTS  #  #  #
if not os.path.isdir('./data'):
    os.mkdir('data')

if not os.path.isfile('./data/prefixes.json'):
    with open("data/prefixes.json", "w") as l:
        l.write('{}')
        l.close()

if not os.path.isfile('./data/stats.json'):
    with open("data/stats.json", "w") as m:
        m.write('{}')
        m.close()

if not os.path.isfile('./crash.0'):
    print('Missing "crash.0" file, where your bot-token is stored')
    sys.exit(1)


#  #  #  REQUIREMENTS  #  #  #


#  #  #  CHECK  #  #  #

def get_prefix(bot, message):
    if message.guild is None:
        prefix = commands.when_mentioned_or("c- ", "c-")(bot, message)

    else:
        with open("data/prefixes.json", "r") as f:
            json_prefixes = json.load(f)

        try:
            get = str(json_prefixes[str(message.guild.id)])
            prefix = commands.when_mentioned_or(f"{get} ", get)(bot, message)

        except KeyError:
            prefix = commands.when_mentioned_or("c- ", "c-")(bot, message)

    return prefix


def get_prefix_tx(bot, message):
    with open("data/prefixes.json", "r") as f:
        prefixes = json.load(f)
    try:
        return prefixes[str(message.guild.id)]
    except KeyError:
        return 'c-'


#  #  #  CHECK  #  #  #

# bot = commands.AutoShardedBot(command_prefix = get_prefix, description = ".", case_insensitive=True) 
bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True)
bot.remove_command('help')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.load_extension('jishaku')


@bot.event
async def on_ready():
    print("Pronto come", bot.user)
    await bot.change_presence(activity=discord.Game(name="c-aiuto"))

    # a = commands.clean_content(use_nicknames=True)
    # message = await a.convert(ctx, message)


#  #  #  EVENTS  #  #  #


@bot.event
async def on_guild_join(guild):
    with open('data/prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = 'c-'

    with open('data/prefixes.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

    ch = bot.get_channel(715151965713072180)
    emb = discord.Embed(
        description=f"<a:YAAY:715156619842814023>\n{bot.user.mention} si è unito al server **{guild.name}**\n proprieatario del server :  **{guild.owner}**\n Membri nel server : **{guild.member_count}**",
        colour=discord.Colour.green())
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
    emb = discord.Embed(
        description=f"<a:SAAD:715156620388335647>\n{bot.user.mention} ha lasciato il server **{guild.name}**\n proprieatario del server :  **{guild.owner}**\n Membri nel server : **{guild.member_count}**",
        colour=discord.Colour.red())
    emb.set_footer(text=f"sono online in {len(bot.guilds)} server", icon_url=bot.user.avatar_url)
    emb.set_thumbnail(url=guild.icon_url)
    if guild.banner:
        emb.set_image(url=guild.banner_url)
    await ch.send(embed=emb)


bot.run(open("crash.0", "r").readline().strip())
