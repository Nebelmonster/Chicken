import json

import discord
from discord import Colour
from discord.ext import commands

async def update_review_embed(x, bot, data):
    channel = bot.get_channel(data["players"][x]["reviewChannel"])
    review_index = data["players"][x]["reviewIndex"]
    submitter = data["order"][review_index]
    if submitter == x:
        data["players"][x]["reviewIndex"] += 1
        submitter = data["order"][review_index + 1]
    embed = discord.Embed(colour=Colour.blue(),
                          title=f"Review Phase! (Song {data["players"][x]["reviewsDone"]}/{data["players"]["playerNum"] - 1})",
                          url=data["players"][submitter]["sub"]["link"])
    embed.add_field(name="Submitter", value=f"```{bot.get_user(int(submitter)).global_name}```", inline=True)
    embed.add_field(name="Song",
                    value=f"```{data["players"][submitter]["sub"]["artist"]} - {data["players"][submitter]["sub"]["titel"]}```",
                    inline=True)
    embed.add_field(name="Link", value=f"```{data["players"][submitter]["sub"]["link"]}```", inline=False)
    embed.add_field(name="Instructions",
                    value=f"```Please send your thoughts and feelings about the song in a single message below.\nThis will be used as your review text later!```",
                    inline=False)
    if bot.get_user(int(submitter)).avatar is not None:
        embed.set_thumbnail(url=bot.get_user(int(submitter)).avatar.url)
    message = await channel.fetch_message(data["players"][x]["reviewMsg"])
    await message.edit(embed=embed)
    data["reviews"][x][submitter] = {}

class ReviewSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if message.guild is None:
            return
        with open("database.json", "r") as file:
            data = json.load(file)
        if message.channel.category_id == 1487953481422602340 and message.channel.id != 1487958792527413418:
            author = str(message.author.id)
            submitter = data["order"][data["players"][author]["reviewIndex"]]

            data["reviews"][author][submitter]["text"] = message.content
            await message.delete()
            await message.channel.send("Review saved!", delete_after=3)
            data["players"][author]["reviewIndex"] += 1
            data["players"][author]["reviewsDone"] += 1

            if data["players"][author]["reviewsDone"] != data["players"]["playerNum"] - 1:
                await update_review_embed(author, self.bot, data)
            with open("database.json", "w") as filee:
                json.dump(data, filee, indent=4)

async def setup(bot):
    await bot.add_cog(ReviewSystem(bot))