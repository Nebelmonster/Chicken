import json
import datetime
import calendar
import math

import discord
from discord import app_commands, Colour
from discord.ext import commands

def get_upcoming_birthdays(num: int, data):
    birthdays = data["birthdays"]
    current_month  = datetime.datetime.now().month
    current_day = datetime.datetime.now().day
    sorted_leaderboard = sorted(birthdays.items(), key=lambda x: (math.fabs(x[1][1] - current_month), math.fabs(x[1][2] - current_day)), reverse=True)
    return sorted_leaderboard[:num]

class BirthdayCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="birthday", description="Birthday")
    @app_commands.guilds(discord.Object(id=1487902534545703072))
    @app_commands.choices(action=[
        app_commands.Choice(name="Set", value="set"),
        app_commands.Choice(name="List", value="list")
    ])
    async def birthday_command(self, interaction, action: app_commands.Choice[str], date: str, user: discord.User = None):
        data = self.bot.data
        member = user or interaction.user
        member_id = str(member.id)
        await interaction.response.defer(ephemeral=True)
        if action.value == "set":
            date_split = date.split(".")
            data["birthdays"][member_id] = [int(date_split[2]), int(date_split[1]), int(date_split[0])]
            await interaction.followup.send("Birthday set.", ephemeral=True)
        elif action.value == "list":
            birthdays = get_upcoming_birthdays(5, data)
            embed = discord.Embed(colour=Colour.purple(), title="Upcoming Birthdays")
            for (user_id, day) in birthdays:
                current_user = self.bot.get_user(int(user_id))
                ordinal = str(day[2]) + ("th" if 4 <= day[2] % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(day[2] % 10, "th"))

                embed.add_field(name=f"{current_user.mention}", value=f"```\n{calendar.month_name[day[1]]} {ordinal}\n```", inline=False)
            await interaction.followup.send(embed=embed)
        with open("database.json", "w") as filee:
            json.dump(data, filee, indent=4)




async def setup(bot):
    await bot.add_cog(BirthdayCommand(bot))