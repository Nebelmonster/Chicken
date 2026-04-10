import json

import discord
from discord import Colour
from discord.ext import commands


class EndCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def end(self, ctx):
        data = self.bot.data
        if ctx.author.id != 294941635505029141:
            await ctx.message.delete()
            await ctx.send(
                "https://tenor.com/view/sarahmcfadyen-atc-against-the-current-chrissy-costanza-middle-finger-gif-26482117",
                delete_after=5)
            return
        if not data["gameloop"]["join"]:
            await ctx.send("The joining phase isn't running!", delete_after=3)
            await ctx.message.delete()
        else:
            await ctx.channel.purge(limit=2)
            channel = await ctx.channel.category.create_text_channel("submissions")
            await channel.send(f"{self.bot.get_guild(1487902534545703072).get_role(1487952220208107742).mention}")
            embed = discord.Embed(colour=Colour.blue(), title="The Submission Phase Has Started!")
            embed.add_field(name="", value="```\nPlease send the song you wanna submit in the following style:\n```",
                            inline=False)
            embed.add_field(name="", value="```yaml\nATC - Heavenly - https://examplelink.com\n```", inline=False)
            embed.add_field(name="",
                            value="```\nYou can only submit one song and cannot change it afterwards\nSo choose carefully!\n```",
                            inline=False)
            embed.add_field(name="Submissions", value=f"**```ml\n0/{data["players"]["playerNum"]}\n```**", inline=False)
            message = await channel.send(embed=embed)

            data["gameloop"]["join"] = False
            data["gameloop"]["sub"] = True
            data["ids"]["subChannel"] = channel.id
            data["ids"]["subMsg"] = message.id
            data["players"]["subNum"] = 0
            with open("database.json", "w") as filee:
                json.dump(data, filee, indent=4)

async def setup(bot):
    await bot.add_cog(EndCommand(bot))