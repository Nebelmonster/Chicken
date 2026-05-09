import discord
from discord import app_commands
from discord.ext import commands


class AddLyricCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addlyric", description="Adds a song to the database")
    @app_commands.default_permissions(administrator=True)
    @app_commands.guilds(discord.Object(id=1487902534545703072))
    async def addlyric_command(self, interaction, song: str, artist: str):
        await interaction.response.defer()
        data = self.bot.data
        data["songs"].append(f"{song.lower()} - {artist.lower()}")
        await interaction.followup.send(f"Added {song.lower()} by {artist.lower()}")

async def setup(bot):
    await bot.add_cog(AddLyricCommand(bot))