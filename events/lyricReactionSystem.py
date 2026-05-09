import random
import lyricsgenius

from discord.ext import commands


class LyricReactionSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if message.guild is None:
            return
        data = self.bot.data
        songs = data
        for song in songs:
            title = song.split(" - ")[0]
            artist = song.split(" - ")[1]
            if song in message.content.lower():
                token = "83lKwQdp5pfGc3e2o7PdOFvsAmKngN583fZY3eWtxcEVLH3Rm4eswujKYElmNm8b"
                genius = lyricsgenius.Genius(token)
                genius.remove_section_headers = True
                lines = genius.search_song(title, artist).lyrics.split("\n")
                rand = random.randrange(0, len(lines))
                await message.channel.send(lines[rand])


async def setup(bot):
    await bot.add_cog(LyricReactionSystem(bot))