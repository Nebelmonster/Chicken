import json

import discord
from discord import Colour
from discord.ext import commands


class RatingSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if message.guild is None:
            return
        data = self.bot.data
        if message.channel.category_id == 1487953481422602340 and message.channel.id != 1487958792527413418 and message.channel.id != int(data["ids"]["subChannel"]):
            print("test2")
            author = str(message.author.id)
            if data["players"][author]["reviewsDone"] == data["players"]["playerNum"] - 1:
                print("test")

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
    await bot.add_cog(RatingSystem(bot))