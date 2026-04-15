import json
import datetime
import calendar

import discord
from discord import app_commands, Colour
from discord.ext import commands

def get_upcoming_birthdays(num: int, data):
    birthdays = data["birthdays"]
    current  = datetime.datetime.now()
    def func(m, d):
        date = datetime.datetime(current.year, m, d)
        if date < current: date = datetime.datetime(current.year + 1, m, d)
        return date - current
    sorted_leaderboard = sorted(birthdays.items(), key=lambda x: func(x[1][1], x[1][2]))
    return sorted_leaderboard[:num]

class BirthdayCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.birthday_group.guild_ids = [1487902534545703072]

    birthday_group = app_commands.Group(name="birthday", description="Manage birthdays")

    @birthday_group.command(name="set", description="Set a users birthday")
    async def birthday_set(self, interaction, date: str, user: discord.User = None):
        data = self.bot.data
        member = user or interaction.user
        member_id = str(member.id)
        await interaction.response.defer()
        date_split = date.split(".")
        data["birthdays"][member_id] = [int(date_split[2]), int(date_split[1]), int(date_split[0])]
        with open("database.json", "w") as filee:
            json.dump(data, filee, indent=4)
        await interaction.followup.send("Birthday set")

    @birthday_group.command(name="list", description="See upcoming birthdays")
    async def birthday_command(self, interaction):
        data = self.bot.data
        await interaction.response.defer()
        birthdays = get_upcoming_birthdays(5, data)
        embed = discord.Embed(colour=Colour.purple(), title="Upcoming Birthdays")
        for (user_id, day) in birthdays:
            current_user = self.bot.get_user(int(user_id)).global_name
            ordinal = str(day[2]) + ("th" if 4 <= day[2] % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(day[2] % 10, "th"))

            embed.add_field(name=f"{current_user}", value=f"```\n{calendar.month_name[day[1]]} {ordinal}\n```", inline=False)
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BirthdayCommand(bot))