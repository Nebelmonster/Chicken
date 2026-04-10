import asyncio
import json

from discord.ext import commands

class ResetCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def reset(self, ctx):
        data = self.bot.data
        if ctx.author.id != 294941635505029141:
            await ctx.send(
                "https://tenor.com/view/sarahmcfadyen-atc-against-the-current-chrissy-costanza-middle-finger-gif-26482117",
                delete_after=5)
            return
        data["reviews"] = {}
        data["ratings"] = {}
        data["order"] = []
        data["gameloop"]["join"] = False
        data["gameloop"]["sub"] = False
        data["gameloop"]["review"] = False
        data["gameloop"]["rating"] = False
        data["ids"]["subChannel"] = -1
        data["ids"]["subMsg"] = -1
        data["players"] = {}
        data["players"]["playerNum"] = 0
        data["players"]["subNum"] = 0
        with open("database.json", "w") as filee:
            json.dump(data, filee, indent=4)
        await ctx.message.delete()
        await ctx.channel.send(f"Resetting data...")
        for x in ctx.guild.get_channel(1487958792527413418).category.text_channels:
            if not x.id == 1487958792527413418:
                await x.delete()
        await ctx.channel.send(f"Data reset successfully!")
        await asyncio.sleep(3)
        await ctx.channel.purge(limit=2)

async def setup(bot):
    await bot.add_cog(ResetCommand(bot))