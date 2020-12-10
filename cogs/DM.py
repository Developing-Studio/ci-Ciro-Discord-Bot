from io import BytesIO
from data.var import *
import aiohttp
import discord
from discord.ext import commands


async def send_message(channel, message):
    if message.attachments:
        filename = message.attachments[0].filename
        attachment = message.attachments[0].url
        async with aiohttp.ClientSession() as session:
            async with session.get(attachment) as resp:
                image_bytes = await resp.read()
        file = discord.File(BytesIO(image_bytes), filename=filename)
        await channel.send(f'> `{message.author}`\n{message.content}', file=file)
    else:
        await channel.send(f'> `{message.author}`\n{message.content}')


async def channel_module(bot, message):
    if not discord.utils.get(bot.get_guild(ciro_guild).channels, name=f'{message.author.id}'):
        overwrites = {
            bot.get_guild(ciro_guild).default_role: discord.PermissionOverwrite(read_messages=False),
            bot.get_guild(ciro_guild).me: discord.PermissionOverwrite(read_messages=True)
        }
        category = discord.utils.get(bot.get_guild(ciro_guild).categories, name=f'DMs TO {bot.user}')
        if str(category) == 'None':
            overwrites = {
                bot.get_guild(ciro_guild).default_role: discord.PermissionOverwrite(read_messages=False),
                bot.get_guild(ciro_guild).me: discord.PermissionOverwrite(read_messages=True)
            }
            await bot.get_guild(ciro_guild).create_category(f'DMs TO {bot.user}', overwrites=overwrites)

        category = discord.utils.get(bot.get_guild(ciro_guild).categories, name=f'DMs TO {bot.user}')

        return await bot.get_guild(ciro_guild).create_text_channel(f'{message.author.id}', overwrites=overwrites,
                                                                   category=category, topic=f'{message.author.name}')
    elif discord.utils.get(bot.get_guild(ciro_guild).channels, name=f'{message.author.id}'):
        return discord.utils.get(bot.get_guild(ciro_guild).channels, name=f'{message.author.id}')


class DM(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            await self.bot.wait_until_ready()
            if type(message.channel) == discord.channel.DMChannel:
                await send_message(await channel_module(self.bot, message), message)
            elif str(message.channel.category) == f'DMs TO {self.bot.user}' and message.guild.id == ciro_guild:
                try:
                    channel = self.bot.get_user(int(message.channel.name))
                    await send_message(channel, message)
                except discord.Forbidden or AttributeError:
                    await message.channel.send('`Non ho più contatti con questo utente` '
                                               'O `L\' utente blocca i messaggi privati`')



def setup(bot):
    bot.add_cog(DM(bot))
