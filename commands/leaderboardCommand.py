import math

import discord
from discord import app_commands, Colour
from discord.ext import commands

def get_level(user_id, data):
    xp = data["counters"][str(user_id)]["msgs"]["xp"]
    return int(math.sqrt(xp / 160) + 1)

def get_xp_leaderboard(num: int, data):
    counters = data["counters"]
    sorted_leaderboard = sorted(counters.items(), key=lambda x: (x[1]["msgs"]["xp"], x[1]["msgs"]["count"]), reverse=True)
    return sorted_leaderboard[:num]

def get_chicken_leaderboard(num: int, data):
    counters = data["counters"]
    sorted_leaderboard = sorted(counters.items(), key=lambda x: x[1]["chicken"], reverse=True)
    return sorted_leaderboard[:num]

class LeaderboardCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    lb_group = app_commands.Group(name="leaderboard", description="Shows leaderboards", guild_ids=[1487902534545703072])

    @lb_group.command(name="chicken", description="Shows the leaderboard")
    async def leaderboard_chicken(self, interaction, lb_type: app_commands.Choice[str]):
        data = self.bot.data
        await interaction.response.defer()
        leaderboard = get_chicken_leaderboard(5, data)
        embed = discord.Embed(colour=Colour.purple(), title="Chicken Leaderboard")
        for rank, (user_id, stats) in enumerate(leaderboard, start=1):
            chicken = stats["chicken"]
            user_name = self.bot.get_user(int(user_id)).global_name
            embed.add_field(name=f"{rank}. {user_name}", value=f"```\n🐔: {chicken}\n```", inline=False)
        await interaction.followup.send(embed=embed)

    @lb_group.command(name="xp", description="Shows the leaderboard")
    async def leaderboard_xp(self, interaction, lb_type: app_commands.Choice[str]):
        data = self.bot.data
        await interaction.response.defer()
        leaderboard = get_xp_leaderboard(5, data)
        embed = discord.Embed(colour=Colour.purple(), title="XP Leaderboard")
        for rank, (user_id, stats) in enumerate(leaderboard, start=1):
            xp = stats["msgs"]["xp"]
            level = get_level(user_id, data)
            user_name = self.bot.get_user(int(user_id)).global_name
            embed.add_field(name=f"{rank}. {user_name}", value=f"```\nLevel: {level} | XP: {xp}\n```", inline=False)
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(LeaderboardCommand(bot))