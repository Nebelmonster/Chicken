import json
import lyricsgenius

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
        with open("lyrics.json", "r") as file:
            data = json.load(file)
        token = "83lKwQdp5pfGc3e2o7PdOFvsAmKngN583fZY3eWtxcEVLH3Rm4eswujKYElmNm8b"
        genius = lyricsgenius.Genius(token)
        genius.remove_section_headers = True
        song = genius.search_song(song, artist)
        if song:
            lyrics = song.lyrics.split("\n")
            await interaction.followup.send(lyrics[0])
        else:
            await interaction.followup.send("Song not found")

async def setup(bot):
    await bot.add_cog(AddLyricCommand(bot))