import json
import discord
from discord.ext import commands


class blacklist(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def bot_check(self, ctx):
        await self.bot.wait_until_ready()
        if not hasattr(self.bot, 'blacklisted'):
            return True
        if str(ctx.command) == 'appeal':
            return True
        if ctx.author.id in self.bot.blacklisted:
            if ctx.author.id in self.bot.IDs:
                await ctx.message.add_reaction('🔥')
                return True
            raise commands.CheckFailure(message="blacklist")

        return True

    async def q_blacklist(self, bot, action: str = None, ID: int = None):
        if action == 'load':
            try:
                with open('./data/blacklist.json', 'r') as file_blacklist:
                    self.bot.blacklisted = json.load(file_blacklist)['blacklisted']
                    return self.bot.blacklisted
            except FileNotFoundError:
                with open('./data/blacklist.json', 'w') as file_blacklist:
                    data = {'blacklisted': []}
                    json.dump(data, file_blacklist)
                    self.bot.blacklisted = []
                    return self.bot.blacklisted
        if action == 'add':
            with open('./data/blacklist.json', 'r') as file_blacklist:
                data = json.load(file_blacklist)
                if ID not in data['blacklisted']:
                    data['blacklisted'].append(ID)
                    self.bot.blacklisted = data['blacklisted']
                else:
                    return 'Utente già nella blacklist'
            with open("./data/blacklist.json", "w") as file_blacklist:
                json.dump(data, file_blacklist)
            return 'Aggiunto con successo'
        if action == 'remove':
            with open('./data/blacklist.json', 'r') as file_blacklist:
                data = json.load(file_blacklist)
                if ID in data['blacklisted']:
                    data['blacklisted'].remove(ID)
                    self.bot.blacklisted = data['blacklisted']
                else:
                    return 'L\'Utente non è nella blacklist'
            with open("./data/blacklist.json", "w") as file_blacklist:
                json.dump(data, file_blacklist)
            return 'Rimosso con successo'

    @commands.Cog.listener()
    async def on_ready(self):
        x = await self.bot.application_info()
        self.bot.IDs = [ID.id for ID in x.team.members]
        await self.q_blacklist(action='load', bot=self.bot)

    @commands.command(hidden=True)
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.user)
    async def appeal(self, ctx, *, appeal_reason):
        if ctx.author.id in self.bot.blacklisted:
            await ctx.send(f"La tua richiesta è stata inviata al proprietario del bot!")
            channel = self.bot.get_channel(747131037397811230)
            embed = discord.Embed(title="", description="New appeal", color=discord.Color.dark_green())
            embed.set_author(name="Ciro appeal system")
            embed.add_field(name=f"Appeal:", value=f"{appeal_reason}", inline=False)
            await channel.send(embed=embed)
            await channel.send(f"This appeal is by {ctx.author.mention}")
        else:
            return await ctx.send(f"{ctx.author.mention}, non sei nella blacklist")

    @appeal.error
    async def appeal_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title="", colour=discord.Colour.red())
            embed.add_field(name="Manca il motivo della tua richiesta\nriprova tra 1 minuto",
                            value=f"```Esempio:\nappeal 'motivo della richiesta'```", inline=False)
            await ctx.send(embed=embed)
        elif isinstance(error, commands.errors.CommandOnCooldown):
            embed = discord.Embed(title=f"Riprova tra {int(error.retry_after)} sec", colour=discord.Colour.red())
            await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def blacklist(self, ctx, action: str = None, member=None, content=None):
        if not action:
            lista = await self.q_blacklist(action='load', bot=self.bot)
            f = '```diff\n- UTENTI NELLA BLACKLIST -```'
            for x in lista:
                user = self.bot.get_user(x)
                if user:
                    f += f'{user}\n'
                else:
                    f += f'{x}\n'
            await ctx.send(f)

        elif member:
            try:
                member = member.replace('<@!', '').replace('>', '')
                memberx = self.bot.get_user(int(member))
                ID = memberx.id
            except:
                if len(member) == 18:
                    ID = int(member)
                else:
                    return await ctx.send('Invalid ID')

            if action in ['aggiungi', 'add']:
                await ctx.send(await self.q_blacklist(action='add', ID=ID, bot=self.bot))
            if action in ['rimuovi', 'remove']:
                lmao = await self.q_blacklist(action='remove', ID=ID, bot=self.bot)
                await ctx.send(lmao)
                try:
                    if lmao == 'Rimosso con successo' and content:
                        embed = discord.Embed(title=content, colour=discord.Colour.red())
                        await self.bot.get_user(ID).send(embed=embed)
                except:
                    pass




def setup(bot):
    bot.add_cog(blacklist(bot))
