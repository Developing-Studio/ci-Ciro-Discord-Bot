import unicodedata
import aiohttp
import discord
from discord.ext import commands, tasks

from Ciro import get_prefix_tx
from data import skyshit24
from gtts import gTTS
import re
from io import BytesIO
from tempfile import TemporaryFile
from PIL import Image, ImageFilter, ImageDraw, ImageFont
import numpy as np


class CharImage:
    def __init__(self, char, *, font, weight=None, pos=(0, 0)):
        CHAR_SIZE = (8, 16)
        image = Image.new("L", CHAR_SIZE, 0)
        draw = ImageDraw.Draw(image)
        draw.text(pos, char, font=font, fill=255)
        self.weight = weight or 1
        self.raw = np.where(np.array(image) > 127, 1, 0)
        self.sum_raw = np.sum(self.raw)

    def compare(self, other, inverse_weight):
        rating = 0
        inverse_rating = 0
        rating = np.sum(self.raw * other)
        inverse_rating = self.sum_raw - rating
        rating = (rating - inverse_weight * inverse_rating) * self.weight
        return rating


def setup_ascii_chars():
    chars = {}
    CHAR_SIZE = (8, 16)
    size = int(CHAR_SIZE[0] / 0.5894)
    font = ImageFont.truetype("data/consola.ttf", size)
    ts = font.getsize("A")
    from_top = (CHAR_SIZE[1] - ts[1] - 1) // 2
    for c in (
            " ", "'", "(", ")", "*", "+", ",", "-", ".", "/", ":", ";", "<", "=", ">", "?", "A", "C", "D", "H", "I",
            "J", "K", "L", "M", "N", "O", "S", "T", "U", "V", "W", "X", "Y", "Z", "[", "\\", "]", "^", "_", "|", "~"
    ):
        chars[c] = CharImage(c, font=font, pos=(0, from_top))

    chars["\\"].weight = 1.8
    chars["/"].weight = 1.8
    chars["_"].weight = 1.8
    chars["-"].weight = 1.8
    chars["<"].weight = 1.3
    chars[">"].weight = 1.3
    chars["|"].weight = 1.8
    chars["("].weight = 1.4
    chars[")"].weight = 1.4
    chars[";"].weight = 0.7
    chars["["].weight = 0.6
    chars["]"].weight = 0.6
    chars["~"].weight = 0.6
    chars["*"].weight = 0.6

    for c in ("A", "C", "D", "H", "I", "J", "K", "L", "M", "N", "O", "S", "T", "U", "V", "W", "X", "Y", "Z"):
        chars[c].weight = 0.6


def lstrip_generator(generator):
    check = True
    for item in generator:
        if check:
            if not item:
                continue
            else:
                yield item
                check = False
        else:
            yield item


def generate_blank_char():
    while True:
        yield "\u2002"
        yield "\u2003"


def get_params(threshold, size):

    width, sep, height = size.partition("x")

    width = int(width.strip())
    height = int(height.strip())

    return threshold, width, height


def convert_image_to_ascii(image, image_proc, per_cut, width, height, char_width, char_height, threshold,
                           inverse):
    width = width
    height = height
    char_width = char_width
    char_height = char_height
    full_width = width * char_width
    full_height = height * char_height

    raw = []
    image = image.resize((full_width, full_height)).convert("L")
    if image_proc:
        image = image_proc(image)
    raw_pixels = np.array(image)
    pixels = np.where(raw_pixels > threshold, 1 - inverse, inverse)
    range_height = range(char_height)
    range_width = range(char_width)

    for y in range(0, full_height, char_height):
        for x in range(0, full_width, char_width):
            cut = pixels[y:y + char_height, x:x + char_width]
            raw.append(per_cut(cut))

    t = lstrip_generator(("".join(raw[i:i + width]).rstrip() for i in range(0, width * height, width)))
    return "\n".join(t)


class divertente(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='Manda informazioni dal mondo')
    async def news(self, ctx):
        text = skyshit24.news_picker()
        embed = discord.Embed(title=text, colour=discord.Colour.blue())
        embed.set_footer(text="https://t.me/skyshit24")
        await ctx.send(embed=embed)

    @commands.command(description='Invia un file mp3 con il testo che hai scritto')
    async def tts(self, ctx, *, message=None):
        if message:
            try:
                message = await commands.clean_content(use_nicknames=True).convert(ctx, message)
                message = re.sub("<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>", "", message)
                message = message.replace('@', '')
                tts = gTTS(text=message, lang='it')
                f = TemporaryFile()
                tts.write_to_fp(f)
                f.seek(0)  # file object
                await ctx.send(file=discord.File(BytesIO(f.read()), filename='tts.mp3'))
                f.close()
            except:
                await ctx.send('Cè qualcosa che non va...')
        else:
            await ctx.send(f'Esempio:\n{get_prefix_tx(self.bot, message=ctx.message)}tts Ciao CIRO')

    @commands.command(aliases=['trig', 'trigg', 'trigger'], description='Crea una gif triggered su un avatar')
    async def triggered(self, ctx, *, member: discord.Member = None):
        """Powered by <https://some-random-api.ml/>"""

        async with ctx.typing():
            member = member or ctx.author
            url = "https://some-random-api.ml/canvas/triggered?avatar=" + str(member.avatar_url_as(format="png"))

            async with aiohttp.ClientSession() as fy:
                async with fy.get(url) as r:
                    res = await r.read()

            await ctx.send(file=discord.File(fp=BytesIO(res), filename=f"{member.display_name}.gif"))

    @commands.command(description='Overlay WASTED di GTA su un avatar')
    async def wasted(self, ctx, *, member: discord.Member = None):
        """Powered by <https://some-random-api.ml/>"""

        async with ctx.typing():
            member = member or ctx.author
            url = "https://some-random-api.ml/canvas/wasted?avatar=" + str(member.avatar_url_as(format="png"))

            async with aiohttp.ClientSession() as fy:
                async with fy.get(url) as r:
                    res = await r.read()

            await ctx.send(file=discord.File(fp=BytesIO(res), filename=f"{member.display_name}.png"))

    @commands.command(description='Crea un immagine ascii')
    async def ascii(self, ctx, *, data: discord.Member = None):
        target = data or ctx.author
        DOT_PATTERN = (1, 4, 2, 5, 3, 6, 7, 8)
        blank_chars = generate_blank_char()

        threshold, width, height = get_params(128, "56x32")

        await ctx.trigger_typing()
        async with aiohttp.ClientSession() as a:
            r = await a.get(str(target.avatar_url_as(format="png")))
            b = await r.read()

        bytes_ = b
        try:
            image = Image.open(BytesIO(bytes_))
        except OSError:
            return await ctx.send("Cannot identify image.")

        def per_cut(cut):
            cut = cut.flatten()
            pos = [str(p) for i, p in enumerate(DOT_PATTERN) if cut[i] == 1]
            if pos:
                pos.sort()
                return unicodedata.lookup(f"BRAILLE PATTERN DOTS-{''.join(pos)}")
            else:
                return next(blank_chars)

        result = await self.bot.loop.run_in_executor(None, convert_image_to_ascii, image, None, per_cut, width,
                                                     height, 2, 4, threshold, 0)
        if result.isspace():
            await ctx.send("Result is all blank. Maybe you should try tweaking threshold a little?")
        else:
            await ctx.send(f"\u200b{result}")


def setup(bot):
    bot.add_cog(divertente(bot))
