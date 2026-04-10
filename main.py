import asyncio
import json
import math

import discord
from discord import Colour
from discord import app_commands
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

def get_level(user_id):
    xp = data["counters"][str(user_id)]["msgs"]["xp"]
    return int(math.sqrt(xp / 160) + 1)


def get_next_level_thresh(user_id):
    next_level = get_level(user_id) + 1
    next_level_threshold = 160 * math.pow(next_level - 1, 2)
    return int(next_level_threshold)


def get_xp_leaderboard(num: int):
    counters = data["counters"]
    sorted_leaderboard = sorted(counters.items(), key=lambda x: (x[1]["msgs"]["xp"], x[1]["msgs"]["count"]), reverse=True)
    return sorted_leaderboard[:num]

def get_chicken_leaderboard(num: int):
    counters = data["counters"]
    sorted_leaderboard = sorted(counters.items(), key=lambda x: x[1]["chicken"], reverse=True)
    return sorted_leaderboard[:num]


with open("database.json", "r") as file:
    data = json.load(file)

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree
bot.data = data

async def my_setup():
    await bot.load_extension("events.backupSystem")
    await bot.load_extension("events.counterSystem")
    await bot.load_extension("events.submissionSystem")
    await bot.load_extension("events.reviewRatingSystem")
    await tree.sync(guild=discord.Object(id=1487902534545703072))
    print("Ready")

bot.setup_hook = my_setup

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
            await interaction.response.send_message(f"<@{interaction.user.id}> you already joined!", delete_after=3)

@bot.command()
async def purge(ctx, number: int):
    await ctx.channel.purge(limit=number+1)
    await ctx.send(f"<@{ctx.author.id}> deleted {number} messages", delete_after=3)

@bot.command()
async def start(ctx):
    await ctx.message.delete()
    if ctx.author.id != 294941635505029141:
        await ctx.send("https://tenor.com/view/sarahmcfadyen-atc-against-the-current-chrissy-costanza-middle-finger-gif-26482117", delete_after=5)
        return
    if not data["gameloop"]["join"]:
        await ctx.send(view=Join())
        data["gameloop"]["join"] = True
        data["players"]["playerNum"] = 0
        with open("database.json", "w") as filee:
            json.dump(data, filee, indent=4)
    else:
        await ctx.send("The joining phase is already running!", delete_after=3)

@bot.command()
async def end(ctx):
    if ctx.author.id != 294941635505029141:
        await ctx.message.delete()
        await ctx.send("https://tenor.com/view/sarahmcfadyen-atc-against-the-current-chrissy-costanza-middle-finger-gif-26482117", delete_after=5)
        return
    if not data["gameloop"]["join"]:
        await ctx.send("The joining phase isn't running!", delete_after=3)
        await ctx.message.delete()
    else:
        await ctx.channel.purge(limit=2)
        channel = await ctx.channel.category.create_text_channel("submissions")
        await channel.send(f"{bot.get_guild(1487902534545703072).get_role(1487952220208107742).mention}")
        embed = discord.Embed(colour=Colour.blue(), title="The Submission Phase Has Started!")
        embed.add_field(name="", value="```\nPlease send the song you wanna submit in the following style:\n```", inline=False)
        embed.add_field(name="", value="```yaml\nATC - Heavenly - https://examplelink.com\n```", inline=False)
        embed.add_field(name="", value="```\nYou can only submit one song and cannot change it afterwards\nSo choose carefully!\n```", inline=False)
        embed.add_field(name="Submissions", value=f"**```ml\n0/{data["players"]["playerNum"]}\n```**", inline=False)
        message = await channel.send(embed=embed)

        data["gameloop"]["join"] = False
        data["gameloop"]["sub"] = True
        data["ids"]["subChannel"] = channel.id
        data["ids"]["subMsg"] = message.id
        data["players"]["subNum"] = 0
        with open("database.json", "w") as filee:
            json.dump(data, filee, indent=4)

@bot.command()
async def reset(ctx):
    if ctx.author.id != 294941635505029141:
        await ctx.send("https://tenor.com/view/sarahmcfadyen-atc-against-the-current-chrissy-costanza-middle-finger-gif-26482117", delete_after=5)
        return
    data["reviews"] = {}
    data["ratings"] = {}
    data["order"] = []
    data["gameloop"]["join"] = False
    data["gameloop"]["sub"] = False
    data["gameloop"]["review"] = False
    data["gameloop"]["rating"] = False
    data["ids"]["subChannel"] = -1
    data["ids"]["subMsg"] = -1
    data["players"] = {}
    data["players"]["playerNum"] = 0
    data["players"]["subNum"] = 0
    with open("database.json", "w") as filee:
        json.dump(data, filee, indent=4)
    await ctx.message.delete()
    await ctx.channel.send(f"Resetting data...")
    for x in ctx.guild.get_channel(1487958792527413418).category.text_channels:
        if not x.id == 1487958792527413418:
            await x.delete()
    await ctx.channel.send(f"Data reset successfully!")
    await asyncio.sleep(3)
    await ctx.channel.purge(limit=2)

@tree.command(
    name="level",
    description="Shows your level",
    guild=discord.Object(id=1487902534545703072)
)
async def level_command(interaction, user: discord.User = None):
    member = user or interaction.user
    if member == bot.user:
        await interaction.response.send_message("Can't use this command on me 😉", ephemeral=True)
        return
    id = member.id
    xp = data["counters"][str(id)]["msgs"]["xp"]
    embed = discord.Embed(colour=Colour.green(), title=f"{member.global_name}'s stats:")
    if str(id) in data["counters"]:
        embed.add_field(name="Level", value=f"```yaml\n{get_level(id)}\n```", inline=False)
        embed.add_field(name="XP", value=f"```yaml\n{xp}/{get_next_level_thresh(id)}\n```", inline=False)
        embed.add_field(name="🐔", value=f"```yaml\n{data["counters"][str(id)]["chicken"]}\n```", inline=False)
    else:
        embed.add_field(name="", value="```\nThis player has not sent a message in this server yet\n```")
    if member.avatar is not None:
        embed.set_thumbnail(url=member.avatar.url)
    await interaction.response.send_message(embed=embed)

@tree.command(
    name="leaderboard",
    description="Shows the XP leaderboard",
    guild=discord.Object(id=1487902534545703072)
)
@app_commands.choices(lb_type=[
    app_commands.Choice(name="XP", value="xp"),
    app_commands.Choice(name="Chicken", value="chicken")
])
async def leaderboard_command(interaction, lb_type: app_commands.Choice[str]):
    await interaction.response.defer()
    if lb_type.value == "xp":
        leaderboard = get_xp_leaderboard(5)
        embed = discord.Embed(colour=Colour.purple(), title="XP Leaderboard")
        for rank, (user_id, stats) in enumerate(leaderboard, start=1):
            xp = stats["msgs"]["xp"]
            level = get_level(user_id)
            user_name = bot.get_user(int(user_id)).global_name
            embed.add_field(name=f"{rank}. {user_name}", value=f"```\nLevel: {level} | XP: {xp}\n```", inline=False)
    else:
        leaderboard = get_chicken_leaderboard(5)
        embed = discord.Embed(colour=Colour.purple(), title="Chicken Leaderboard")
        for rank, (user_id, stats) in enumerate(leaderboard, start=1):
            chicken = stats["chicken"]
            user_name = bot.get_user(int(user_id)).global_name
            embed.add_field(name=f"{rank}. {user_name}", value=f"```\n🐔: {chicken}\n```", inline=False)
    await interaction.followup.send(embed=embed)

@tree.command(
    name="say",
    description="Lets the bot say something",
    guild=discord.Object(id=1487902534545703072)
)
@app_commands.default_permissions(administrator=True)
async def say_command(interaction: discord.Interaction, msg: str):
    await interaction.response.defer(ephemeral=True)
    await interaction.channel.send(msg)
    await interaction.delete_original_response()

if __name__ == "__main__":
    bot.run(token, log_handler=handler, log_level=logging.DEBUG)