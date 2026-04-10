import json
import math
import random
import time

import discord
from discord import Colour
from discord.ext import commands

MIN_XP = 3
MAX_XP = 7
COOLDOWN = 15

def get_level(user_id, data):
    xp = data["counters"][str(user_id)]["msgs"]["xp"]
    return int(math.sqrt(xp / 160) + 1)


def get_next_level_thresh(user_id,  data):
    next_level = get_level(user_id, data) + 1
    next_level_threshold = 160 * math.pow(next_level - 1, 2)
    return int(next_level_threshold)

class CounterSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if message.guild is None:
            return
        with open("database.json", "r") as file:
            data = json.load(file)
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
            if data["counters"][id_str]["msgs"]["xp"] + rndm >= get_next_level_thresh(id_str, data):
                embed = discord.Embed(colour=Colour.red())
                embed.add_field(name="", value=f"```\nYou reached level {get_level(id_str, data) + 1}!\n```")
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