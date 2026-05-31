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
        if artist.lower() == "taylor swift":
            await interaction.followup.send("Fuck you. Jumpy is mine now!!")
            return
        for s in data["songs"]:
            if f"{song.lower()} - " in s:
                artist_old = s.split(" - ")[1]

                class Confirm(discord.ui.View):
                    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
                    async def on_yes(self, b_interaction, button):
                        if b_interaction.user != interaction.user:
                            return
                        data["songs"].append(f"{song.lower()} - {artist.lower()}")
                        with open("database.json", "w") as filee:
                            json.dump(data, filee, indent=4)
                        await b_interaction.response.edit_message(content=f"Added {song.lower()} by {artist.lower()}", view=None)
                    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
                    async def on_no(self, b_interaction, button):
                        if b_interaction.user != interaction.user:
                            return
                        await b_interaction.response.edit_message(content="Song discarded.", view=None)

                await interaction.followup.send(f"A song with that title already exists in the database:\n`{song.lower()} by {artist_old.lower()}`\nDo you still want to proceed?", view=Confirm())
                return
        data["songs"].append(f"{song.lower()} - {artist.lower()}")
        with open("database.json", "w") as filee:
            json.dump(data, filee, indent=4)
        await interaction.followup.send(content=f"Added {song.lower()} by {artist.lower()}")
    @group.command(name="remove", description="Adds a song")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_command(self, interaction, song: str):
        await interaction.response.defer()
        data = self.bot.data
        artist = ""
        match_list = []
        for s in data["songs"]:
            if f"{song.lower()} - " in s:
                match_list.append(s)
        length = len(match_list)
        if length == 1:
            data["songs"].remove(match_list[0])
            artist = match_list[0].split(" - ")[1]
            with open("database.json", "w") as filee:
                json.dump(data, filee, indent=4)
            await interaction.followup.send(f"Removed {song.lower()} by {artist.lower()}")
        elif length >= 2:

            class artistB(discord.ui.View):
                def __init__(self, data):
                    super().__init__()
                    self.data = data

                    for i, x in enumerate(match_list):
                        button = discord.ui.Button(
                            label=x.split(" - ")[1],
                            style=discord.ButtonStyle.green,
                            custom_id=f"rate_button_{i}"
                        )
                        button.callback = self.create_callback(x.split(" - ")[1], button)
                        self.add_item(button)

                def create_callback(self, label_value, button):
                    async def callback(b_interaction: discord.Interaction):
                        if b_interaction.user != interaction.user:
                            return
                        data["songs"].remove(f"{song.lower()} - {label_value.lower()}")
                        with open("database.json", "w") as filee:
                            json.dump(data, filee, indent=4)
                        await b_interaction.response.edit_message(content=f"Removed {song.lower()} by {label_value.lower()}", view=None)
                    return callback
            await interaction.followup.send("Found multiple songs with that title in the database.\nWhich one do you want to remove?", view=artistB(data))

        else:
            await interaction.followup.send("No song with that title in the database")
            return

async def setup(bot):
    await bot.add_cog(AddLyricCommand(bot))