import discord
from discord import app_commands
from discord.ext import commands


class SayCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @app_commands.command(name="say", description="Lets the bot say something")
    @app_commands.default_permissions(administrator=True)
    @app_commands.guilds(discord.Object(id=1487902534545703072))
    async def say_command(self, interaction: discord.Interaction, msg: str):
        await interaction.response.defer(ephemeral=True)
        await interaction.channel.send(msg)
        await interaction.delete_original_response()

async def setup(bot):
    await bot.add_cog(SayCommand(bot))