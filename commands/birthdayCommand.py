import json
import time

import discord
from discord import app_commands
from discord.ext import commands


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
        await interaction.response.defer()
        if action.value == "set":
            data["birthdays"][member_id] = time.strptime(date, "%d.%m.%Y")
            with open("database.json", "w") as filee:
                json.dump(data, filee, indent=4)
            interaction.followup.send("Birthday set.", ephemeral=True)



async def setup(bot):
    await bot.add_cog(BirthdayCommand(bot))