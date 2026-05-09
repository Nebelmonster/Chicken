import json
import random

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
        with open("lyrics.json", "r") as file:
            data = json.load(file)
        for song in data:
            if song in message.content.lower():
                lines = data[song]
                rand = random.randrange(0, len(lines))
                await message.channel.send(lines[rand])


async def setup(bot):
    await bot.add_cog(LyricReactionSystem(bot))