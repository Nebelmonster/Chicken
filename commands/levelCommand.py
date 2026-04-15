from utils import get_level, get_next_level_thresh

import discord
from discord import app_commands, Colour
from discord.ext import commands


class LevelCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @app_commands.command(name="level", description="Shows your level")
    @app_commands.guilds(discord.Object(id=1487902534545703072))
    async def level_command(self, interaction, user: discord.User = None):
        data = self.bot.data
        member = user or interaction.user
        if member == self.bot.user:
            await interaction.response.send_message("Can't use this command on me 😉", ephemeral=True)
            return
        id = member.id
        xp = data["counters"][str(id)]["msgs"]["xp"]
        embed = discord.Embed(colour=Colour.green(), title=f"{member.global_name}'s stats:")
        if str(id) in data["counters"]:
            embed.add_field(name="Level", value=f"```yaml\n{get_level(id, data)}\n```", inline=False)
            embed.add_field(name="XP", value=f"```yaml\n{xp}/{get_next_level_thresh(id, data)}\n```", inline=False)
            embed.add_field(name="🐔", value=f"```yaml\n{data["counters"][str(id)]["chicken"]}\n```", inline=False)
        else:
            embed.add_field(name="", value="```\nThis player has not sent a message in this server yet\n```")
        if member.avatar is not None:
            embed.set_thumbnail(url=member.avatar.url)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(LevelCommand(bot))