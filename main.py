import asyncio
import json
import random
import math
import time

import discord
from discord import Colour
from discord import app_commands
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

lock = asyncio.Lock()

def get_level(user_id):
    xp = data["counters"][str(user_id)]["msgs"]["xp"]
    return int(math.sqrt(xp / 100) + 1)

def get_next_level_thresh(user_id):
    next_level = get_level(user_id) + 1
    next_level_threshold = 100 * math.pow(next_level - 1, 2)
    return int(next_level_threshold)

async def update_review_embed(x):
    channel = bot.get_channel(data["players"][x]["reviewChannel"])
    review_index = data["players"][x]["reviewIndex"]
    submitter = data["order"][review_index]
    if submitter == x:
        data["players"][x]["reviewIndex"] += 1
        submitter = data["order"][review_index + 1]
    embed = discord.Embed(colour=Colour.blue(),
                          title=f"Review Phase! (Song {data["players"][x]["reviewsDone"]}/{data["players"]["playerNum"] - 1})",
                          url=data["players"][submitter]["sub"]["link"])
    embed.add_field(name="Submitter", value=f"```{bot.get_user(int(submitter)).global_name}```", inline=True)
    embed.add_field(name="Song",
                    value=f"```{data["players"][submitter]["sub"]["artist"]} - {data["players"][submitter]["sub"]["titel"]}```",
                    inline=True)
    embed.add_field(name="Link", value=f"```{data["players"][submitter]["sub"]["link"]}```", inline=False)
    embed.add_field(name="Instructions",
                    value=f"```Please send your thoughts and feelings about the song in a single message below.\nThis will be used as your review text later!```",
                    inline=False)
    if bot.get_user(int(submitter)).avatar is not None:
        embed.set_thumbnail(url=bot.get_user(int(submitter)).avatar.url)
    message = await channel.fetch_message(data["players"][x]["reviewMsg"])
    await message.edit(embed=embed)
    data["reviews"][x][submitter] = {}

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

tree = bot.tree

with open("database.json", "r") as file:
    data = json.load(file)

@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=1487902534545703072))
    print(f"We are ready to go in, {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.guild is None:
        return
    if not str(message.author.id) in data["counters"]:
        data["counters"][str(message.author.id)] = {}
        data["counters"][str(message.author.id)]["chicken"] = 0
        data["counters"][str(message.author.id)]["msgs"] = {}
        data["counters"][str(message.author.id)]["msgs"]["count"] = 0
        data["counters"][str(message.author.id)]["msgs"]["xp"] = 0
    data["counters"][str(message.author.id)]["msgs"]["count"] += 1
    if (not "lastMsg" in data["counters"][str(message.author.id)]["msgs"]) or (time.time() - data["counters"][str(message.author.id)]["msgs"]["lastMsg"] > 10):
        rndm = random.randint(3,7)
        if data["counters"][str(message.author.id)]["msgs"]["xp"] + rndm >= get_next_level_thresh(message.author.id):
            message.reply(f"You reached level {get_level(message.author.id) + 1}")
        data["counters"][str(message.author.id)]["msgs"]["xp"] += rndm
        data["counters"][str(message.author.id)]["msgs"]["lastMsg"] = time.time()
    if "chicken" in message.content.lower() or "🐔" in message.content.lower():
        await message.add_reaction("🐔")
        data["counters"][str(message.author.id)]["chicken"] += 1
    with open("database.json", "w") as filee:
        json.dump(data, filee, indent=4)

    #Submission Phase

    if message.channel.id == data["ids"]["subChannel"]:
        async with lock:
            data["players"][str(message.author.id)]["sub"] = {}
            sub = message.content.split(" - ")
            data["players"][str(message.author.id)]["sub"]["artist"] = sub[0]
            data["players"][str(message.author.id)]["sub"]["titel"] = sub[1]
            data["players"][str(message.author.id)]["sub"]["link"] = sub[2]
            data["players"]["subNum"] += 1
            with open("database.json", "w") as filee:
                json.dump(data, filee, indent=4)
            await message.channel.set_permissions(message.author, send_messages=False)
            await message.delete()
            await message.channel.send(f"{message.author.mention} Submission saved!", delete_after=3)

            message = await message.channel.fetch_message(data["ids"]["subMsg"])
            embed_edit = discord.Embed(colour=Colour.blue(), title="The Submission Phase Has Started!")
            embed_edit.add_field(name="", value="```\nPlease send the song you wanna submit in the following style:\n```", inline=False)
            embed_edit.add_field(name="", value="```yaml\nATC - Heavenly - https://examplelink.com\n```", inline=False)
            embed_edit.add_field(name="", value="```\nYou can only submit one song and cannot change it afterwards\nSo choose carefully!\n```", inline=False)
            embed_edit.add_field(name="Submissions", value=f"**```ml\n{data["players"]["subNum"]}/{data["players"]["playerNum"]}\n```**", inline=False)
            await message.edit(embed=embed_edit)

            if data["players"]["subNum"] == data["players"]["playerNum"]:
                role = bot.get_guild(1487902534545703072).get_role(1487952220208107742)
                for x in data["players"]:
                    if x != "playerNum" and x != "subNum":
                        data["order"].append(x)
                        data["players"][x]["reviewIndex"] = 0
                        user = bot.get_user(int(x))
                        overwrites = {
                            user: discord.PermissionOverwrite(read_messages=True),
                            bot.get_guild(1487902534545703072).default_role: discord.PermissionOverwrite(read_messages=False)
                        }
                        channel = await message.channel.category.create_text_channel(f"{user.global_name}-reviews", overwrites=overwrites)
                        data["players"][x]["reviewChannel"] = channel.id
                        data["players"][x]["reviewsDone"] = 0
                        data["reviews"][x] = {}
                await message.channel.send(f"{role.mention}")
                embed = discord.Embed(colour=Colour.blue() ,title="Every Player Submitted Their Song!")
                embed.add_field(name="", value="```\nBelow this channel you should now see a channel called \n[Your Name]-reviews\nGo there for further information!\n```", inline=False)
                await message.channel.send(embed=embed)
                data["gameloop"]["sub"] = False
                data["gameloop"]["review"] = True
                with open("database.json", "w") as filee:
                    json.dump(data, filee, indent=4)


        #Review Phase
                for x in data["players"]:
                    if x == "playerNum" or x == "subNum":
                        continue
                    channel = bot.get_channel(data["players"][x]["reviewChannel"])
                    review_index = data["players"][x]["reviewIndex"]
                    submitter = data["order"][review_index]
                    if submitter == x:
                        data["players"][x]["reviewIndex"] += 1
                        submitter = data["order"][review_index + 1]
                    embed = discord.Embed(colour=Colour.blue(), title=f"Review Phase! (Song {data["players"][x]["reviewsDone"]}/{data["players"]["playerNum"] - 1})", url=data["players"][submitter]["sub"]["link"])
                    embed.add_field(name="Submitter", value=f"```{bot.get_user(int(submitter)).global_name}```", inline=True)
                    embed.add_field(name="Song", value=f"```{data["players"][submitter]["sub"]["artist"]} - {data["players"][submitter]["sub"]["titel"]}```", inline=True)
                    embed.add_field(name="Link", value=f"```{data["players"][submitter]["sub"]["link"]}```", inline=False)
                    embed.add_field(name="Instructions", value=f"```Please send your thoughts and feelings about the song in a single message below.\nThis will be used as your review text later!```", inline=False)
                    if bot.get_user(int(submitter)).avatar is not None:
                        embed.set_thumbnail(url=bot.get_user(int(submitter)).avatar.url)
                    embed_msg = await channel.send(embed=embed)
                    data["players"][x]["reviewMsg"] = embed_msg.id
                    data["reviews"][x][submitter] = {}

                    with open("database.json", "w") as filee:
                        json.dump(data, filee, indent=4)

    elif message.channel.category_id == 1487953481422602340 and message.channel.id != 1487958792527413418:
        author = str(message.author.id)
        submitter = data["order"][data["players"][author]["reviewIndex"]]

        data["reviews"][author][submitter]["text"] = message.content
        await message.delete()
        await message.channel.send("Review saved!", delete_after=3)
        data["players"][author]["reviewIndex"] += 1
        data["players"][author]["reviewsDone"] += 1

        if data["players"][author]["reviewsDone"] != data["players"]["playerNum"] - 1:
            await update_review_embed(author)
        else:

            #Rating Phase

            data["gameloop"]["review"] = False
            data["gameloop"]["rating"] = True

            class rateB(discord.ui.View):
                def __init__(self, data):
                    super().__init__()
                    self.data = data

                    for i, x in enumerate(data["order"]):
                        if i == 0:
                            continue

                        button = discord.ui.Button(
                            label=str(i),
                            style=discord.ButtonStyle.green,
                            custom_id=f"rate_button_{i}"
                        )
                        button.callback = self.create_callback(i, button)
                        self.add_item(button)

                def create_callback(self, label_value, button):
                    async def callback(interaction: discord.Interaction):
                        user_id = str(interaction.user.id)
                        if user_id not in self.data["ratings"]:
                            self.data["ratings"][user_id] = []

                        mem = ""
                        index = 0
                        for y in self.data["order"]:
                            if y == user_id:
                                continue
                            if index == int(label_value) - 1:
                                mem = y
                            index += 1

                        self.data["ratings"][user_id].append(mem)

                        with open("database.json", "w") as filee:
                            json.dump(self.data, filee, indent=4)
                        button.disabled = True
                        await interaction.response.edit_message(view=self)
                        await interaction.followup.send(f"Rating saved!", ephemeral=True)
                    return callback

            embed = discord.Embed(colour=Colour.blue(), title="Rating Phase!")
            embed.add_field(name="You have reviewed all entries!", value=f"```\nBelow there is a list of all entries numbered from 1 - {data["players"]["playerNum"]-1}\nClick the buttons corresponding to the entry in the order from best to worst!\nSo if you like entry 2 the most, click button 2 first.\n```")
            i = 1
            for x in data["order"]:
                if x == author:
                    continue
                embed.add_field(name=f"{i}. {data["players"][x]["sub"]["artist"]} - {data["players"][x]["sub"]["titel"]}", value = f"```\n{data["players"][x]["sub"]["link"]}\n```", inline=False)
                i += 1
            embed_msg = await message.channel.fetch_message(data["players"][author]["reviewMsg"])
            await embed_msg.edit(embed=embed, view=rateB(data))

        with open("database.json", "w") as filee:
            json.dump(data, filee, indent=4)


    await bot.process_commands(message)

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
    id = member.id
    xp = data["counters"][str(id)]["msgs"]["xp"]
    embed = discord.Embed(colour=Colour.green(), title=f"{member.global_name}'s stats:")
    embed.add_field(name="Level", value=f"```yaml\n{get_level(id)}\n```", inline=False)
    embed.add_field(name="XP", value=f"```yaml\n{xp}/{get_next_level_thresh(id)}\n```", inline=False)
    if member.avatar is not None:
        embed.set_thumbnail(url=member.avatar.url)
    await interaction.response.send_message(embed=embed)

@tree.command(
    name="say",
    description="Lets the bot say something",
    guild=discord.Object(id=1487902534545703072),
)
@app_commands.default_permissions(administrator=True)
async def say_command(interaction: discord.Interaction, msg: str):
    await interaction.response.defer(ephemeral=True)
    await interaction.channel.send(msg)
    await interaction.delete_original_response()

bot.run(token, log_handler=handler, log_level=logging.DEBUG)