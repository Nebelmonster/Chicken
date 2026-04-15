import json
import datetime

import discord
from discord import app_commands
from discord.ext import commands

def get_upcoming_birthdays(num: int, data):
    birthdays = data["birthdays"]
    sorted_leaderboard = sorted(birthdays.items(), key=lambda x: x[1]["chicken"], reverse=True)
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
    async def birthday_command(self, interaction, action: app_commands.Choice[str], date: str, user:  int):
        data = self.bot.data
        #member = user or interaction.user
        #member_id = str(member.id)
        member_id = user
        await interaction.response.defer(ephemeral=True)
        if action.value == "set":
            date_split = date.split(".")
            data["birthdays"][member_id] = datetime.datetime(int(date_split[2]), int(date_split[1]), int(date_split[0]))
            await interaction.followup.send("Birthday set.", ephemeral=True)
        with open("database.json", "w") as filee:
            json.dump(data, filee, indent=4)




async def setup(bot):
    await bot.add_cog(BirthdayCommand(bot))