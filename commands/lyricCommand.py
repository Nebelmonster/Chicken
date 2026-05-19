import json

import discord
from discord import app_commands
from discord.ext import commands


class AddLyricCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    group = app_commands.Group(name="lyric", description="Adds or removes songs", guild_ids=[1487902534545703072])

    @group.command(name="add", description="Adds a song")
    async def add_command(self, interaction, song: str, artist: str):
        await interaction.response.defer()
        data = self.bot.data
        for s in data["songs"]:
            if f"{song.lower()} - " in s:

                class Confirm(discord.ui.View):
                    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
                    async def on_yes(self, b_interaction, button):
                        data["songs"].append(f"{song.lower()} - {artist.lower()}")
                        with open("database.json", "w") as filee:
                            json.dump(data, filee, indent=4)
                        for b in b_interaction.components:
                            if b.type == discord.InteractionButton:
                                b.disabled = True
                        await b_interaction.followup.send(f"Added {song.lower()} by {artist.lower()}")
                    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
                    async def on_yes(self, b_interaction, button):
                        for b in b_interaction.components:
                            if b.type == discord.InteractionButton:
                                b.disabled = True
                        await b_interaction.followup.send("Song has been discarded")

                await interaction.followup.send(f"A song with that title already exists in the database: {song.lower()} by {artist.lower()}. Do you still want to proceed?", view=Confirm())

    @group.command(name="remove", description="Adds a song")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_command(self, interaction, song: str):
        await interaction.response.defer()
        data = self.bot.data
        artist = ""
        for s in data["songs"]:
            if f"{song.lower()} - " in s:
                data["songs"].remove(s)
                artist = song.split(" - ")[1]
                break
        if artist == "":
            await interaction.followup.send("No song with that title in the database")
            return
        with open("database.json", "w") as filee:
            json.dump(data, filee, indent=4)
        await interaction.followup.send(f"Removed {song.lower()} by {artist.lower()}")

async def setup(bot):
    await bot.add_cog(AddLyricCommand(bot))