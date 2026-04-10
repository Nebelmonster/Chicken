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
    @app_commands.command(name="leaderboard", description="Shows the leaderboard")
    @app_commands.choices(lb_type=[
        app_commands.Choice(name="XP", value="xp"),
        app_commands.Choice(name="Chicken", value="chicken")
    ])
    async def leaderboard_command(self, interaction, lb_type: app_commands.Choice[str]):
        data = self.bot.data
        await interaction.response.defer()
        if lb_type.value == "xp":
            leaderboard = get_xp_leaderboard(5, data)
            embed = discord.Embed(colour=Colour.purple(), title="XP Leaderboard")
            for rank, (user_id, stats) in enumerate(leaderboard, start=1):
                xp = stats["msgs"]["xp"]
                level = get_level(user_id, data)
                user_name = self.bot.get_user(int(user_id)).global_name
                embed.add_field(name=f"{rank}. {user_name}", value=f"```\nLevel: {level} | XP: {xp}\n```", inline=False)
        else:
            leaderboard = get_chicken_leaderboard(5, data)
            embed = discord.Embed(colour=Colour.purple(), title="Chicken Leaderboard")
            for rank, (user_id, stats) in enumerate(leaderboard, start=1):
                chicken = stats["chicken"]
                user_name = self.bot.get_user(int(user_id)).global_name
                embed.add_field(name=f"{rank}. {user_name}", value=f"```\n🐔: {chicken}\n```", inline=False)
        await interaction.followup.send(embed=embed)

async def setup(bot):
    bot.add_cog(LeaderboardCommand(bot))