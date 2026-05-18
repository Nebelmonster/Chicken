import random
import lyricsgenius

from discord.ext import commands

def get_line_index(lines, length):
    rand = random.randrange(0, length)
    if lines[rand] == "" or lines[rand] == ")" or lines[rand] == "(":
        lines.pop(rand)
        return get_line_index(lines, length - 1)
    else:
        return rand

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
        songs = data["songs"]
        for song in songs:
            title = song.split(" - ")[0]
            artist = song.split(" - ")[1]
            if title in message.content.lower():
                token = "83lKwQdp5pfGc3e2o7PdOFvsAmKngN583fZY3eWtxcEVLH3Rm4eswujKYElmNm8b"
                genius = lyricsgenius.Genius(token)
                genius.remove_section_headers = True
                lines = genius.search_song(title, artist).lyrics.split("\n")
                line_index = get_line_index(lines, len(lines))
                line = lines[line_index].replace("(", "").replace(")", "")
                await message.channel.send(lines[line_index])


async def setup(bot):
    await bot.add_cog(LyricReactionSystem(bot))