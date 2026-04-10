import json

import discord
from discord.ext import commands


class StartCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    async def start(self, ctx):
        data = self.bot.data
        await ctx.message.delete()
        if ctx.author.id != 294941635505029141:
            await ctx.send(
                "https://tenor.com/view/sarahmcfadyen-atc-against-the-current-chrissy-costanza-middle-finger-gif-26482117",
                delete_after=5)
            return

        class Join(discord.ui.View):
            @discord.ui.button(label="Click to join!", style=discord.ButtonStyle.green)
            async def on_join(self, interaction, button):
                if str(interaction.user.id) not in data["players"]:
                    data["players"][str(interaction.user.id)] = {}
                    data["players"]["playerNum"] += 1
                    with open("database.json", "w") as filee:
                        json.dump(data, filee, indent=4)
                    role = interaction.guild.get_role(1487952220208107742)
                    await interaction.user.add_roles(role, reason="Joined the game")
                    await interaction.response.send_message(f"<@{interaction.user.id}> you are in!", delete_after=3)
                else:
                    await interaction.response.send_message(f"<@{interaction.user.id}> you already joined!",
                                                            delete_after=3)

        if not data["gameloop"]["join"]:
            await ctx.send(view=Join())
            data["gameloop"]["join"] = True
            data["players"]["playerNum"] = 0
            with open("database.json", "w") as filee:
                json.dump(data, filee, indent=4)
        else:
            await ctx.send("The joining phase is already running!", delete_after=3)

async def setup(bot):
    bot.add_cog(StartCommand(bot))