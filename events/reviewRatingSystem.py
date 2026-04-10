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
                          title=f"Review Phase! (Song {data["players"][x]["reviewsDone"] + 1}/{data["players"]["playerNum"] - 1})",
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



class ReviewRatingSystem(commands.cog.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if message.guild is None:
            return
        data = self.bot.data
        if message.channel.category_id == 1487953481422602340 and message.channel.id != 1487958792527413418 and message.channel.id != int(
                data["ids"]["subChannel"]):
            author = str(message.author.id)
            submitter = data["order"][data["players"][author]["reviewIndex"]]

            data["reviews"][author][submitter]["text"] = message.content
            await message.delete()
            await message.channel.send("Review saved!", delete_after=3)
            data["players"][author]["reviewIndex"] += 1
            data["players"][author]["reviewsDone"] += 1

            if data["players"][author]["reviewsDone"] != data["players"]["playerNum"] - 1:
                await update_review_embed(author, self.bot, data)
            else:

                class rateB(discord.ui.View):
                    def __init__(self, data):
                        super().__init__()
                        self.data = data

                        for i, x in enumerate(data["order"]):
                            if i == 0:
                                continue

                            button = discord.ui.Button(
                                label=str(i),
                                style=discord.ButtonStyle.green,
                                custom_id=f"rate_button_{i}"
                            )
                            button.callback = self.create_callback(i, button)
                            self.add_item(button)

                    def create_callback(self, label_value, button):
                        async def callback(interaction: discord.Interaction):
                            user_id = str(interaction.user.id)
                            if user_id not in self.data["ratings"]:
                                self.data["ratings"][user_id] = []

                            mem = ""
                            index = 0
                            for y in self.data["order"]:
                                if y == user_id:
                                    continue
                                if index == int(label_value) - 1:
                                    mem = y
                                index += 1

                            self.data["ratings"][user_id].append(mem)

                            with open("database.json", "w") as filee:
                                json.dump(self.data, filee, indent=4)
                            button.disabled = True
                            await interaction.response.edit_message(view=self)
                            await interaction.followup.send(f"Rating saved!", ephemeral=True)

                        return callback

                embed = discord.Embed(colour=Colour.blue(), title="Rating Phase!")
                embed.add_field(name="You have reviewed all entries!",
                                value=f"```\nBelow there is a list of all entries numbered from 1 - {data["players"]["playerNum"] - 1}\nClick the buttons corresponding to the entry in the order from best to worst!\nSo if you like entry 2 the most, click button 2 first.\n```")
                i = 1
                for x in data["order"]:
                    if x == author:
                        continue
                    embed.add_field(
                        name=f"{i}. {data["players"][x]["sub"]["artist"]} - {data["players"][x]["sub"]["titel"]}",
                        value=f"```\n{data["players"][x]["sub"]["link"]}\n```", inline=False)
                    i += 1
                embed_msg = await message.channel.fetch_message(data["players"][author]["reviewMsg"])
                await embed_msg.edit(embed=embed, view=rateB(data))
            with open("database.json", "w") as filee:
                json.dump(data, filee, indent=4)

async def setup(bot):
    await bot.add_cog(ReviewRatingSystem(bot))