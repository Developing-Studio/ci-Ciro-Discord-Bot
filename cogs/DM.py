from io import BytesIO

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


class DM(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.BOT_GUILD_FOR_DM = 714802740345176074

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            await self.bot.wait_until_ready()
            if type(message.channel) == discord.channel.DMChannel:
                if not discord.utils.get(self.bot.get_guild(self.BOT_GUILD_FOR_DM).channels, name=f'{message.author.id}'):
                    overwrites = {
                        self.bot.get_guild(self.BOT_GUILD_FOR_DM).default_role: discord.PermissionOverwrite(read_messages=False),
                        self.bot.get_guild(self.BOT_GUILD_FOR_DM).me: discord.PermissionOverwrite(read_messages=True)
                    }
                    category = discord.utils.get(self.bot.get_guild(self.BOT_GUILD_FOR_DM).categories, name=f'DMs TO {self.bot.user}')
                    if str(category) == 'None':
                        overwrites = {
                            self.bot.get_guild(self.BOT_GUILD_FOR_DM).default_role: discord.PermissionOverwrite(
                                read_messages=False),
                            self.bot.get_guild(self.BOT_GUILD_FOR_DM).me: discord.PermissionOverwrite(
                                read_messages=True)
                        }
                        await self.bot.get_guild(self.BOT_GUILD_FOR_DM).create_category(f'DMs TO {self.bot.user}', overwrites=overwrites)

                    category = discord.utils.get(self.bot.get_guild(self.BOT_GUILD_FOR_DM).categories, name=f'DMs TO {self.bot.user}')

                    channel = await self.bot.get_guild(self.BOT_GUILD_FOR_DM).create_text_channel(f'{message.author.id}', overwrites=overwrites, category=category, topic=f'{message.author.name}')
                    await send_message(channel, message)
                elif discord.utils.get(self.bot.get_guild(self.BOT_GUILD_FOR_DM).channels, name=f'{message.author.id}'):
                    channel = discord.utils.get(self.bot.get_guild(self.BOT_GUILD_FOR_DM).channels, name=f'{message.author.id}')
                    await send_message(channel, message)
            elif str(message.channel.category) == f'DMs TO {self.bot.user}':
                try:
                    channel = self.bot.get_user(int(message.channel.name))
                    await send_message(channel, message)
                except discord.Forbidden or AttributeError:
                    await message.channel.send('`Non ho più contatti con questo utente` O `L\' utente blocca i messaggi privati`')


def setup(bot):
    bot.add_cog(DM(bot))
