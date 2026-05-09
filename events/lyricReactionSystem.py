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
        if "heavenly" in message.content.lower():
            with open("heavenly.json", "r") as file:
                data = json.load(file)
            lines = data["lyrics"]
            rand = random.randrange(0, len(lines))
            await message.channel.send(lines[rand])
            with open("heavenly.json", "w") as filee:
                json.dump(data, filee, indent=4)


async def setup(bot):
    await bot.add_cog(LyricReactionSystem(bot))