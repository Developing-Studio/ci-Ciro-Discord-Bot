import asyncio
import re
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

        self.volume = 40
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

    __slots__ = ('requester', )

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
                                                      password="IT | Kewai#9029", identifier=self.bot.user, region='eu_central')

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
                        return await ctx.send('Non trovo nessuna canzone!')

                    player = self.bot.wavelink.get_player(ctx.guild.id)
                    if not player.is_connected:
                        await ctx.invoke(self.connect_)
                        tracks_welcome = await self.bot.wavelink.get_tracks('https://www.youtube.com/watch?v=jLtbFWJm9_M')
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
                        await ctx.send(f'Ho aggiunto {len(tracks.tracks)} alla coda.')
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

                    vol = max(min(vol, 200), 0)
                    controller.volume = vol

                    await ctx.send(f'Ho impostato il volume a `{vol}/200`')
                    await player.set_volume(vol)
                else:
                    await ctx.send('Sei mutato, anche se modificassi il volume non sentiresti nulla!')
            except AttributeError:
                await ctx.send('Non sei connesso a nessun canale vocale!')

    @commands.command(aliases=['np', 'current', 'nowplaying', 'come', 'titolo'], description='Ti dice il titolo del brano in riproduzione')
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

    @commands.command(aliases=['q', 'queue', 'c'], description='Serve a vedere la coda di riproduzione')
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

    @commands.command(aliases=['disconnect', 'disconnetti', 'leave', 'l'], description='Serve a disconnettere il bot da un canale vocale nel server')
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

                await player.stop()
                await player.disconnect()
                await ctx.send('Mi sono disconnesso con successo.')
        except AttributeError:
            await ctx.send('Non sei connesso a nessun canale vocale!')

    @commands.command(description='Cerca un brano su yt')
    @commands.bot_has_permissions(embed_links=True)
    async def yt(self, ctx, *, query):
        embed = discord.Embed(title=f"Ho trovato questi risultati per: {query}", color=0xd629c9)
        query = await self.bot.wavelink.get_tracks(f'ytsearch: {query}')

        for track in query[0:9]:
            embed.add_field(name=f"{track}", value=u'\u200b', inline=False)

        await ctx.send(embed=embed)

    @commands.command(hidden=True, aliases=['act'], description='Mostra in quali server si sta ascoltando musica')
    @commands.bot_has_permissions(embed_links=True)
    @commands.is_owner()
    async def activity(self, ctx):
        embed = discord.Embed(title=f"La gente sta ascoltando musica in questi server:", color=0xd629c9)
        for x in self.controllers:
            embed.add_field(name=f" ឵឵", value=f'[{x}](https://discordapp.com/channels/{x})', inline=False)
        await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(music(bot))
