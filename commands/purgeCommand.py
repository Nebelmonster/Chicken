from discord.ext import commands


class PurgeCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    async def purge(self, ctx, number: int):
        await ctx.channel.purge(limit=number + 1)
        await ctx.send(f"<@{ctx.author.id}> deleted {number} messages", delete_after=3)

async def setup(bot):
    await bot.add_cog(PurgeCommand(bot))