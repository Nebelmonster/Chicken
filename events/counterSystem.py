import json
import random
import time

import discord
from discord import Colour
from discord.ext import commands
from main import data, get_level, get_next_level_thresh

MIN_XP = 3
MAX_XP = 7
COOLDOWN = 15

class CounterSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if message.guild is None:
            return
        id_str = str(message.author.id)
        if not id_str in data["counters"]:
            data["counters"][id_str] = {}
            data["counters"][id_str]["chicken"] = 0
            data["counters"][id_str]["msgs"] = {}
            data["counters"][id_str]["msgs"]["count"] = 0
            data["counters"][id_str]["msgs"]["xp"] = 0
            data["counters"][id_str]["msgs"]["lastMsg"] = 0
        data["counters"][id_str]["msgs"]["count"] += 1
        if time.time() - data["counters"][id_str]["msgs"]["lastMsg"] > COOLDOWN:
            rndm = random.randint(MIN_XP, MAX_XP)
            if data["counters"][id_str]["msgs"]["xp"] + rndm >= get_next_level_thresh(id):
                embed = discord.Embed(colour=Colour.red())
                embed.add_field(name="", value=f"```\nYou reached level {get_level(id) + 1}!\n```")
                await message.reply(embed=embed)
            data["counters"][id_str]["msgs"]["xp"] += rndm
            data["counters"][id_str]["msgs"]["lastMsg"] = time.time()
        if "chicken" in message.content.lower() or "🐔" in message.content.lower():
            await message.add_reaction("🐔")
            data["counters"][id_str]["chicken"] += 1
        with open("database.json", "w") as filee:
            json.dump(data, filee, indent=4)

async def setup(bot):
    await bot.add_cog(CounterSystem(bot))