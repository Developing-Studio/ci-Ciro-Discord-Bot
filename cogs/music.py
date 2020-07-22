import asyncio
import json
import random
import re

import aiohttp
import requests
import wavelink
import discord
import itertools
from discord.ext import commands
from typing import Union, Any

RURL = re.compile(r'https?:\/\/(?:www\.)?.+')


class QueueControl:
    def __init__(self, bot, guild_id):
        self.bot = bot
        self.guild_id = guild_id
        self.channel = None

        self.next = asyncio.Event()
        self.queue = asyncio.Queue()

        self.volume = 20
        self.now_playing = None

        self.bot.loop.create_task(self.controller_loop())

    async def controller_loop(self):
        await self.bot.wait_until_ready()

        player = self.bot.wavelink.get_player(self.guild_id)
        await player.set_volume(self.volume)

        while True:
            if self.now_playing:
                await self.now_playing.delete()

            self.next.clear()

            song = await self.queue.get()
            await player.play(song)
            self.now_playing = await self.channel.send(f'In Riproduzione: `{song}`')

            await self.next.wait()


class Track(wavelink.Track):
    """Wavelink Track object with a requester attribute."""

    __slots__ = ('requester',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args)

        self.requester = kwargs.get('requester')


class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.controllers = {}

        if not hasattr(bot, 'wavelink'):
            self.bot.wavelink = wavelink.Client(bot=self.bot)

        self.bot.loop.create_task(self.start_nodes())

    async def start_nodes(self):
        await self.bot.wait_until_ready()
        LavaLinkServer = '127.0.0.1'
        # LavaLinkServer = '192.168.1.123'
        nodes = await self.bot.wavelink.initiate_node(host=LavaLinkServer, port=2333,
                                                      rest_uri="http://" + LavaLinkServer + ":2333",
                                                      password="IT | Kewai#9029", identifier=self.bot.user,
                                                      region='eu_central')

        nodes.set_hook(self.on_event_hook)

    async def on_event_hook(self, event):
        if isinstance(event, (wavelink.TrackEnd, wavelink.TrackException)):
            controller = self.get_controller(event.player)
            controller.next.set()

    def get_controller(self, value: Union[commands.Context, wavelink.Player]):
        if isinstance(value, commands.Context):
            gid = value.guild.id
        else:
            gid = value.guild_id

        try:
            controller = self.controllers[gid]
        except KeyError:
            controller = QueueControl(self.bot, gid)
            self.controllers[gid] = controller

        return controller

    @commands.command(name='join', aliases=['j', 'entra'], description='Serve a connettere il bot a un canale vocale')
    async def connect_(self, ctx, *, channel: discord.VoiceChannel = None):
        """Connect to a valid voice channel."""
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                return await ctx.send(
                    'Non ti vedo in nessun canale vocale. Specifica in quale canale devo entrare!')
        if not ctx.author.voice.self_deaf:
            player = self.bot.wavelink.get_player(ctx.guild.id)
            await ctx.send(f'Mi sto collegando in  **`{channel.name}`**')
            await player.connect(channel.id)

            controller = self.get_controller(ctx)
            controller.channel = ctx.channel
        else:
            await ctx.send('Sei mutato, anche se mi connetto non sentiresti la musica!')

    @commands.command(aliases=['p'], description='Serve a riprodurre o a mettere in coda un brano')
    async def play(self, ctx, *, query: str = None):
        if query:
            try:
                if not ctx.author.voice.self_deaf:
                    if not RURL.match(query):
                        query = f'ytsearch:{query}'

                    tracks = await self.bot.wavelink.get_tracks(f'{query}')

                    if not tracks:
                        return await ctx.send('Non trovo nessuna canzone! *Questo comando è  in via di sviluppo, potrebbe funzionare se insisti*')

                    player = self.bot.wavelink.get_player(ctx.guild.id)
                    if not player.is_connected:
                        await ctx.invoke(self.connect_)
                        tracks_welcome = await self.bot.wavelink.get_tracks(
                            'https://www.youtube.com/watch?v=jLtbFWJm9_M')
                        tracks_welcome = tracks_welcome[0]
                        controller = self.get_controller(ctx)
                        await controller.queue.put(tracks_welcome)
                    try:
                        track = tracks[0]

                        controller = self.get_controller(ctx)
                        await controller.queue.put(track)
                        await ctx.send(f'Ho aggiunto {str(track)} brani alla coda.')
                    except TypeError:
                        for track in tracks.tracks:
                            controller = self.get_controller(ctx)
                            track = Track(track.id, track.info, requester=ctx.author)
                            await controller.queue.put(track)
                        await ctx.send(f'Ho aggiunto {len(tracks.tracks)} brani alla coda.')
                else:
                    await ctx.send('Sei mutato, anche se riproducessi un brano non sentiresti nulla!')
            except AttributeError:
                await ctx.send('Non sei connesso a nessun canale vocale!')
        else:
            await ctx.send('Quale brano devo riprodurre/aggiungere in coda?')

    @commands.command(name='pausa', aliases=['pause'], description='Serve a mettere in pausa un brano')
    async def pause(self, ctx):
        try:
            if not ctx.author.voice.self_deaf:
                player = self.bot.wavelink.get_player(ctx.guild.id)
                if not player.is_playing:
                    return await ctx.send('Non sto riproducendo brani!')

                await ctx.send('Ho messo in pausa il brano!')
                await player.set_pause(True)
            else:
                await ctx.send('Sei mutato, anche se mettessi in pausa la riproduzione non sentiresti nulla!')
        except AttributeError:
            await ctx.send('Non sei connesso a nessun canale vocale!')

    @commands.command(aliases=['r', 'resume'], description='Serve a riprendere la riproduzione di un brano')
    async def riprendi(self, ctx):
        try:
            if not ctx.author.voice.self_deaf:
                player = self.bot.wavelink.get_player(ctx.guild.id)
                if not player.paused:
                    return await ctx.send('Attualmente non ho brani in pausa!')

                await ctx.send('Riprendo la riproduzione!')
                await player.set_pause(False)
            else:
                await ctx.send('Sei mutato, anche se riprendessi la riproduzione non sentiresti nulla!')
        except AttributeError:
            await ctx.send('Non sei connesso a nessun canale vocale!')

    @commands.command(aliases=['s', 'skippa'], description='Serve a passare al prossimo brano in coda')
    async def skip(self, ctx):
        try:
            if not ctx.author.voice.self_deaf:
                player = self.bot.wavelink.get_player(ctx.guild.id)

                if not player.is_playing:
                    return await ctx.send('Non sto riproducendo brani!')

                await ctx.send('Passo al brano sucessivo!')
                await player.stop()
            else:
                await ctx.send('Sei mutato, anche se passassi un brano all’altro non sentiresti nulla!')
        except AttributeError:
            await ctx.send('Non sei connesso a nessun canale vocale!')

    @commands.command(aliases=['vol'], description='Serve ad visualizzare, abbassare o alzare il volume')
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def volume(self, ctx, *, vol: int = None):
        """Set the player volume."""
        if not vol:
            player = self.bot.wavelink.get_player(ctx.guild.id)
            await ctx.send(f'Il volume attuale è `{player.volume}/200`')
        else:
            try:
                if not ctx.author.voice.self_deaf:
                    player = self.bot.wavelink.get_player(ctx.guild.id)
                    controller = self.get_controller(ctx)

                    vol = max(min(vol, 100), 0)
                    controller.volume = vol

                    await ctx.send(f'Ho impostato il volume a `{vol}/100`')
                    await player.set_volume(vol)
                else:
                    await ctx.send('Sei mutato, anche se modificassi il volume non sentiresti nulla!')
            except AttributeError:
                await ctx.send('Non sei connesso a nessun canale vocale!')

    @commands.command(aliases=['np', 'current', 'nowplaying', 'come', 'titolo'],
                      description='Ti dice il titolo del brano in riproduzione')
    @commands.bot_has_permissions(embed_links=True)
    async def now_playing(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id)

        if not player.current:
            return await ctx.send('Non sto riproducendo brani!')

        controller = self.get_controller(ctx)
        embed = discord.Embed(title=player.current.title, colour=0xd629c9)
        embed.set_thumbnail(url=player.current.thumb)

        minutes = round((player.current.length / 1000) / 60)

        embed.add_field(name="Durata", value=f"{minutes} minuti")

        await controller.now_playing.delete()

        controller.now_playing = await ctx.send(embed=embed)

    @commands.command(aliases=['lc', 'testo'], description='Mostra il testo del brano in riproduzione')
    async def lyrics(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id)
        # print(player.current.title)
        if '-' in player.current.title:
            async with aiohttp.ClientSession() as a:
                data = player.current.title.split('(')[0].split('feat')[0].split('ft.')[0].split('OFFICIAL')[0].split(
                    'Official')[0].split('- ')
                link = 'https://api.lyrics.ovh/v1/' + data[0] + '/' + data[1]
                # print('try normal')
                # print(link)
                r = await a.get(link)
                b = await r.json()
                try:
                    oof = str(b['lyrics'])
                    oof = oof.split("\n")
                    pag = commands.Paginator(prefix=None, suffix=None)
                    for a in oof:
                        pag.add_line(a)
                    for a in pag.pages:
                        await ctx.send(a)
                        await asyncio.sleep(0.5)
                except KeyError:  # try reverse
                    link = 'https://api.lyrics.ovh/v1/' + data[1] + '/' + data[0]
                    # print('try reverse')
                    # print(link)
                    r = await a.get(link)
                    b = await r.json()
                    try:
                        oof = str(b['lyrics'])
                        oof = oof.split("\n")
                        pag = commands.Paginator(prefix=None, suffix=None)
                        for a in oof:
                            pag.add_line(a)
                        for a in pag.pages:
                            await ctx.send(a)
                            await asyncio.sleep(0.5)
                    except KeyError:  # try split , 1
                        link = 'https://api.lyrics.ovh/v1/' + data[0].split(',')[0] + '/' + data[1]
                        # print('try split , 1')
                        # print(link)
                        r = await a.get(link)
                        b = await r.json()
                        try:
                            oof = str(b['lyrics'])
                            oof = oof.split("\n")
                            pag = commands.Paginator(prefix=None, suffix=None)
                            for a in oof:
                                pag.add_line(a)
                            for a in pag.pages:
                                await ctx.send(a)
                                await asyncio.sleep(0.5)
                        except KeyError:  # try split , 2
                            # print('try split 2')
                            link = 'https://api.lyrics.ovh/v1/' + data[0].split(',')[1] + '/' + data[1]
                            # print(link)
                            r = await a.get(link)
                            b = await r.json()
                            try:
                                oof = str(b['lyrics'])
                                oof = oof.split("\n")
                                pag = commands.Paginator(prefix=None, suffix=None)
                                for a in oof:
                                    pag.add_line(a)
                                for a in pag.pages:
                                    await ctx.send(a)
                                    await asyncio.sleep(0.5)
                            except KeyError:  # try split 3
                                # print('try split 3')
                                link = 'https://api.lyrics.ovh/v1/' + data[0].split(',')[2] + '/' + data[1]
                                # print(link)
                                r = await a.get(link)
                                b = await r.json()
                                try:
                                    oof = str(b['lyrics'])
                                    oof = oof.split("\n")
                                    pag = commands.Paginator(prefix=None, suffix=None)
                                    for a in oof:
                                        pag.add_line(a)
                                    for a in pag.pages:
                                        await ctx.send(a)
                                        await asyncio.sleep(0.5)
                                except:
                                    await ctx.send('Non trovo il testo di questo brano')

        else:
            async with aiohttp.ClientSession() as a:
                data = player.current.title.split('(')[0].split('feat')[0].split('ft.')[0].split('- ')
                aut = player.current.author.replace('Official', '').replace('OFFICIAL', '').replace('Vevo', '').replace(
                    'VEVO', '')
                link = 'https://api.lyrics.ovh/v1/' + aut + '/' + data[0]
                r = await a.get(link)
                b = await r.json()
                try:
                    oof = str(b['lyrics'])
                    oof = oof.split("\n")
                    pag = commands.Paginator(prefix=None, suffix=None)
                    for a in oof:
                        pag.add_line(a)
                    for a in pag.pages:
                        await ctx.send(a)
                        await asyncio.sleep(0.5)
                except KeyError:
                    await ctx.send('Non trovo il testo per questo brano')
        # ORIGINAL
        # try:
        # response = requests.get('https://api.lyrics.ovh/v1/' + player.current.author + '/' + player.current.title)
        # json_data = json.loads(response.content)
        # print(player.current.title)
        # print(player.current.author)
        # print(player.current.info)
        # try:
        # lyrics = json_data['lyrics']
        # print(lyrics)  # testo
        # except KeyError:
        # print('not found')
        # except:
        # print('qualcosa non va')

    @commands.group(aliases=['q', 'queue', 'c'], description='Serve a vedere la coda di riproduzione',
                    invoke_without_command=True)
    @commands.bot_has_permissions(embed_links=True)
    async def coda(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id)
        controller: Union[QueueControl, Any] = self.get_controller(ctx)

        if not player.current or not controller.queue._queue:
            return await ctx.send('Non ci sono canzoni in coda!')

        upcoming = list(itertools.islice(controller.queue._queue, 0, 20))

        fmt = '\n'.join(f'**`{str(song)}`**' for song in upcoming)
        embed = discord.Embed(title=f'I prossimi {len(upcoming)} brani', description=fmt)

        await ctx.send(embed=embed)

    #  @coda.command(name='cancella', aliases=['canc', 'delete', 'del', 'svuota', 'reset', 'clear'], description='Svuota la coda di riproduzione')
    #  @commands.cooldown(1, 60, commands.BucketType.user)
    #  async def svuota_subcommand(self, ctx):
    #  try:
    #  if not ctx.author.voice.self_deaf:
    #  try:
    #  del self.controllers[ctx.guild.id]
    #  except KeyError:
    #  return await ctx.send('Non cè niente in coda.')
    #  await ctx.send('Ho cancellato la coda.')
    #  controller = self.get_controller(ctx)
    #  controller.channel = ctx.channel
    #  except AttributeError:
    #  await ctx.send('Non sei connesso a nessun canale vocale!')

    @commands.command(aliases=['disconnect', 'disconnetti', 'leave', 'l'],
                      description='Serve a disconnettere il bot da un canale vocale nel server')
    async def stop(self, ctx):
        """Stop and disconnect the player and controller."""
        try:
            if not ctx.author.voice.self_deaf:
                player = self.bot.wavelink.get_player(ctx.guild.id)

                try:
                    del self.controllers[ctx.guild.id]
                except KeyError:
                    await player.disconnect()
                    return await ctx.send('Non cè niente da stoppare.')

                # await player.stop()
                # await player.disconnect()
                await player.destroy()
                await ctx.send('Mi sono disconnesso con successo.')
        except AttributeError:
            await ctx.send('Non sei connesso a nessun canale vocale!')

    @commands.command(description='Cerca il titolo di un brano su yt')
    @commands.bot_has_permissions(embed_links=True)
    async def yt(self, ctx, *, query=None):
        if query:
            embed = discord.Embed(title=f"Ho trovato questi risultati per: {query}", color=0xd629c9)
            query = await self.bot.wavelink.get_tracks(f'ytsearch: {query}')

            for track in query[0:9]:
                embed.add_field(name=f"{track}", value=u'\u200b', inline=False)

            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="", colour=discord.Colour.red())
            embed.add_field(name="Serve a cercare il titolo esatto di una canzone",
                            value=f'Esempio:\n`{self.bot.command_prefix(self.bot, message=ctx.message)}yt Luca Sarracino`\nSucessivamente facendo copia incolla dal risultato\n`{self.bot.command_prefix(self.bot, message=ctx.message)}play Luca Sarracino feat Elvira Visone " Mi hai rotto il cuore "`',
                            inline=False)
            await ctx.send(embed=embed)

    @commands.command(aliases=['mischia'], description='Serve a vedere la coda di riproduzione')
    @commands.bot_has_permissions(embed_links=True)
    async def shuffle(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id)
        controller: Union[QueueControl, Any] = self.get_controller(ctx)

        if not player.current or not controller.queue._queue:
            return await ctx.send('Non ci sono canzoni in coda!')

        random.shuffle(controller.queue._queue)

        await ctx.send('Ho mischiato la coda!')

    @commands.command(aliases=['eq', 'equalizer'], description="Cambia l'equalizzatore", hidden=True)
    @commands.is_owner()
    async def equalizzatore(self, ctx, *, equalizer: str):
        """Change the players equalizer."""
        player = self.bot.wavelink.get_player(ctx.guild.id)
        controller: Union[QueueControl, Any] = self.get_controller(ctx)

        if not player.is_connected:
            return

        flat = ('flat', 'norm', 'normale', 'spento', 'off')
        boost = ('boost', 'bassi', 'bass')
        metal = 'metal'
        piano = 'piano'

        if equalizer.lower() in flat:
            eq = wavelink.Equalizer.flat()
            await player.set_eq(eq)
            await ctx.send("Ho ripristinato l'equalizzatore", delete_after=15)
        elif equalizer.lower() in boost:
            eq = wavelink.Equalizer.boost()
            await player.set_eq(eq)
            await ctx.send(f'Ho aumentato i bassi!', delete_after=15)
        elif equalizer.lower() == metal:
            eq = wavelink.Equalizer.metal()
            await player.set_eq(eq)
            await ctx.send("Ho impostato un suono metal", delete_after=15)
        elif equalizer.lower() == piano:
            eq = wavelink.Equalizer.piano()
            await player.set_eq(eq)
            await ctx.send("Ho impostato un suono piano(riduce i bassi)", delete_after=15)
        else:
            return await ctx.send(f'Sono disponibili i seguenti parametri: `normale` `bassi` `metal` `piano`')

    @commands.command(aliases=['act'], description='Mostra in quali server si sta ascoltando musica', hidden=True)
    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    async def activity(self, ctx):
        embed = discord.Embed(title=f"La gente sta ascoltando musica in questi server:", color=0xd629c9)
        for x in self.controllers:
            embed.add_field(name=f" ឵឵", value=f'[{x}](https://discordapp.com/channels/{x})', inline=False)
        await ctx.send(embed=embed)

    @commands.command(description="Prova a creare un invito per l'id del server", hidden=True)
    @commands.is_owner()
    async def get(self, ctx, ID=None):
        if ID:
            try:
                ID = int(ID)
            except:
                return await ctx.send("L'ID deve essere un numero")
            g = discord.utils.get(self.bot.guilds, id=ID)
            if any(l.id == ID for l in self.bot.guilds):
                try:
                    for a in g.text_channels:
                        return await ctx.send(await a.create_invite(max_uses=1))
                except:
                    pass
            else:
                await ctx.send('Non sono in quel server')
        else:
            return await ctx.send("Fornisci l'ID")


def setup(bot):
    bot.add_cog(music(bot))
