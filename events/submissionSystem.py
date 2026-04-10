import asyncio
import json

import discord
from discord import Colour
from discord.ext import commands

lock = asyncio.Lock()

class SubmissionSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if message.guild is None:
            return
        data = self.bot.data
        if message.channel.id == data["ids"]["subChannel"]:
            async with lock:
                id_str = str(message.author.id)
                data["players"][id_str]["sub"] = {}
                sub = message.content.split(" - ")
                data["players"][id_str]["sub"]["artist"] = sub[0]
                data["players"][id_str]["sub"]["titel"] = sub[1]
                data["players"][id_str]["sub"]["link"] = sub[2]
                data["players"]["subNum"] += 1
                with open("database.json", "w") as filee:
                    json.dump(data, filee, indent=4)
                await message.channel.set_permissions(message.author, send_messages=False)
                await message.delete()
                await message.channel.send(f"{message.author.mention} Submission saved!", delete_after=3)

                message = await message.channel.fetch_message(data["ids"]["subMsg"])
                embed_edit = discord.Embed(colour=Colour.blue(), title="The Submission Phase Has Started!")
                embed_edit.add_field(name="",
                                     value="```\nPlease send the song you wanna submit in the following style:\n```",
                                     inline=False)
                embed_edit.add_field(name="", value="```yaml\nATC - Heavenly - https://examplelink.com\n```",
                                     inline=False)
                embed_edit.add_field(name="",
                                     value="```\nYou can only submit one song and cannot change it afterwards\nSo choose carefully!\n```",
                                     inline=False)
                embed_edit.add_field(name="Submissions",
                                     value=f"**```ml\n{data["players"]["subNum"]}/{data["players"]["playerNum"]}\n```**",
                                     inline=False)
                await message.edit(embed=embed_edit)

                if data["players"]["subNum"] == data["players"]["playerNum"]:
                    role = self.bot.get_guild(1487902534545703072).get_role(1487952220208107742)
                    for x in data["players"]:
                        if x != "playerNum" and x != "subNum":
                            data["order"].append(x)
                            data["players"][x]["reviewIndex"] = 0
                            user = self.bot.get_user(int(x))
                            overwrites = {
                                user: discord.PermissionOverwrite(read_messages=True),
                                self.bot.get_guild(1487902534545703072).default_role: discord.PermissionOverwrite(
                                    read_messages=False)
                            }
                            channel = await message.channel.category.create_text_channel(f"{user.global_name}-reviews", overwrites=overwrites)
                            data["players"][x]["reviewChannel"] = channel.id
                            data["players"][x]["reviewsDone"] = 0
                            data["reviews"][x] = {}
                    await message.channel.send(f"{role.mention}")
                    embed = discord.Embed(colour=Colour.blue(), title="Every Player Submitted Their Song!")
                    embed.add_field(name="",
                                    value="```\nBelow this channel you should now see a channel called \n[Your Name]-reviews\nGo there for further information!\n```",
                                    inline=False)
                    await message.channel.send(embed=embed)
                    data["gameloop"]["sub"] = False
                    data["gameloop"]["review"] = True
                    with open("database.json", "w") as filee:
                        json.dump(data, filee, indent=4)



                    for x in data["players"]:
                        if x == "playerNum" or x == "subNum":
                            continue
                        channel = self.bot.get_channel(data["players"][x]["reviewChannel"])
                        review_index = data["players"][x]["reviewIndex"]
                        submitter = data["order"][review_index]
                        if submitter == x:
                            data["players"][x]["reviewIndex"] += 1
                            submitter = data["order"][review_index + 1]
                        embed = discord.Embed(colour=Colour.blue(),
                                              title=f"Review Phase! (Song {data["players"][x]["reviewsDone"] + 1}/{data["players"]["playerNum"] - 1})",
                                              url=data["players"][submitter]["sub"]["link"])
                        embed.add_field(name="Submitter", value=f"```{self.bot.get_user(int(submitter)).global_name}```",
                                        inline=True)
                        embed.add_field(name="Song",
                                        value=f"```{data["players"][submitter]["sub"]["artist"]} - {data["players"][submitter]["sub"]["titel"]}```",
                                        inline=True)
                        embed.add_field(name="Link", value=f"```{data["players"][submitter]["sub"]["link"]}```",
                                        inline=False)
                        embed.add_field(name="Instructions",
                                        value=f"```Please send your thoughts and feelings about the song in a single message below.\nThis will be used as your review text later!```",
                                        inline=False)
                        if self.bot.get_user(int(submitter)).avatar is not None:
                            embed.set_thumbnail(url=self.bot.get_user(int(submitter)).avatar.url)
                        embed_msg = await channel.send(embed=embed)
                        data["players"][x]["reviewMsg"] = embed_msg.id
                        data["reviews"][x][submitter] = {}

                        with open("database.json", "w") as filee:
                            json.dump(data, filee, indent=4)

async def setup(bot):
    await bot.add_cog(SubmissionSystem(bot))