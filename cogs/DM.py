import discord
from discord.ext import commands


class DM(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.BOT_GUILD_FOR_DM = 714802740345176074
        self.CATEGORY_NAME_FOR_DM = 'DMs TO CIRO'

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            if type(message.channel) == discord.channel.DMChannel:
                if not discord.utils.get(self.bot.get_guild(self.BOT_GUILD_FOR_DM).channels, name=f'{message.author.id}'):
                    overwrites = {
                        self.bot.get_guild(self.BOT_GUILD_FOR_DM).default_role: discord.PermissionOverwrite(read_messages=False),
                        self.bot.get_guild(self.BOT_GUILD_FOR_DM).me: discord.PermissionOverwrite(read_messages=True)
                    }
                    category = discord.utils.get(self.bot.get_guild(self.BOT_GUILD_FOR_DM).categories, name=self.CATEGORY_NAME_FOR_DM)
                    if str(category) == 'None':
                        await self.bot.get_guild(self.BOT_GUILD_FOR_DM).create_category(self.CATEGORY_NAME_FOR_DM)

                    category = discord.utils.get(self.bot.get_guild(self.BOT_GUILD_FOR_DM).categories, name=self.CATEGORY_NAME_FOR_DM)

                    channel = await self.bot.get_guild(self.BOT_GUILD_FOR_DM).create_text_channel(f'{message.author.id}', overwrites=overwrites, category=category, topic=f'{message.author.name}')
                    member = message.author
                    await channel.send(message.content)
                elif discord.utils.get(self.bot.get_guild(self.BOT_GUILD_FOR_DM).channels, name=f'{message.author.id}'):
                    channel = discord.utils.get(self.bot.get_guild(self.BOT_GUILD_FOR_DM).channels, name=f'{message.author.id}')
                    await channel.send(message.content)
            elif str(message.channel.category) == self.CATEGORY_NAME_FOR_DM:
                try:
                    channel = self.bot.get_user(int(message.channel.name))
                    await channel.send(message.content)
                except discord.Forbidden:
                    await message.channel.send('`Non ho più contatti con questo utente` O `L\' utente blocca i messaggi privati`')


def setup(bot):
    bot.add_cog(DM(bot))
