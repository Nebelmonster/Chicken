import json

import discord
from discord import app_commands
from discord.ext import commands


class AddLyricCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    group = app_commands.Group(name="lyric", description="Adds or removes songs", guild_ids=[1487902534545703072])

    @group.command(name="add", description="Adds a song")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_command(self, interaction, song: str, artist: str):
        await interaction.response.defer()
        data = self.bot.data
        data["songs"].append(f"{song.lower()} - {artist.lower()}")
        with open("database.json", "w") as filee:
            json.dump(data, filee, indent=4)
        await interaction.followup.send(f"Added {song.lower()} by {artist.lower()}")

    @group.command(name="remove", description="Adds a song")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_command(self, interaction, song: str, artist: str):
        await interaction.response.defer()
        data = self.bot.data
        data["songs"].remove(f"{song.lower()} - {artist.lower()}")
        with open("database.json", "w") as filee:
            json.dump(data, filee, indent=4)
        await interaction.followup.send(f"Removed {song.lower()} by {artist.lower()}")

async def setup(bot):
    await bot.add_cog(AddLyricCommand(bot))