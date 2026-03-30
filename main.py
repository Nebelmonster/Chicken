import json
import discord
from discord import Colour
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

with open("database.json", "r") as file:
    data = json.load(file)

@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    #Submission Phase

    if message.channel.id == data["ids"]["subChannel"]:
        data["players"][str(message.author.id)]["sub"] = message.content
        data["players"]["subNum"] += 1
        with open("database.json", "w") as filee:
            json.dump(data, filee, indent=4)
        await message.channel.set_permissions(message.author, send_messages=False)
        await message.delete()
        await message.channel.send(f"{message.author.mention} Submission saved!", delete_after=3)

        message = await message.channel.fetch_message(data["ids"]["subMsg"])
        embed_edit = discord.Embed(colour=Colour.blue(), title="The Submission Phase Has Started!")
        embed_edit.add_field(name="",
                        value="```\nPlease send in the YouTube link of the song you want to submit!\nYou can only submit one song and cannot change it afterwards\nSo choose carefully!\n```",
                        inline=True)
        embed_edit.add_field(name="Submissions", value=f"**```ml\n{data["players"]["subNum"]}/{data["players"]["playerNum"]}\n```**", inline=False)
        await message.edit(embed=embed_edit)

        if data["players"]["subNum"] == data["players"]["playerNum"]:
            role = bot.get_guild(1487902534545703072).get_role(1487952220208107742)
            for x in data["players"]:
                if x != "playerNum" and x != "subNum":
                    user = bot.get_user(int(x))
                    overwrites = {
                        user: discord.PermissionOverwrite(read_messages=True),
                        bot.get_guild(1487902534545703072).default_role: discord.PermissionOverwrite(read_messages=False)
                    }
                    channel = await message.channel.category.create_text_channel(f"{user.name}-reviews", overwrites=overwrites)
                    data["players"][x]["reviewCannel"] = channel.id
            await message.channel.send(f"{role.mention}")
            embed = discord.Embed(colour=Colour.blue() ,title="Every Player Submitted Their Song!")
            embed.add_field(name="", value="```\nBelow this channel you should now see a channel called \n[Your Name]-reviews\nGo there for further information!\n```", inline=False)
            await message.channel.send(embed=embed)
            data["gameloop"]["sub"] = False
            data["gameloop"]["review"] = True
            with open("database.json", "w") as filee:
                json.dump(data, filee, indent=4)

    #Review Phase



    await bot.process_commands(message)

class Join(discord.ui.View):
    @discord.ui.button(label="Click to join!", style=discord.ButtonStyle.green)
    async def on_join(self, interaction, button):
        if str(interaction.user.id) not in data["players"]:
            data["players"][str(interaction.user.id)] = {}
            data["players"]["playerNum"] += 1
            with open("database.json", "w") as filee:
                json.dump(data, filee, indent=4)
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
        embed.add_field(name="", value="```\nPlease send in the YouTube link of the song you want to submit!\nYou can only submit one song and cannot change it afterwards\nSo choose carefully!\n```", inline=True)
        embed.add_field(name="Submissions", value=f"**```ml\n0/{data["players"]["playerNum"]}\n```**", inline=False)
        message = await channel.send(embed=embed)

        data["gameloop"]["join"] = False
        data["gameloop"]["sub"] = True
        data["ids"]["subChannel"] = channel.id
        data["ids"]["subMsg"] = message.id
        data["players"]["subNum"] = 0
        with open("database.json", "w") as filee:
            json.dump(data, filee, indent=4)


bot.run(token, log_handler=handler, log_level=logging.DEBUG)