import json
from datetime import datetime, timedelta

import discord
from discord import app_commands, Colour
from discord.ext import commands, tasks


class ReminderCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_reminders.start()

    @app_commands.command(name="remindme", description="Sets a reminder")
    @app_commands.guilds(discord.Object(id=1487902534545703072))
    async def level_command(self, interaction, time: str, msg: str):
        data = self.bot.data
        now = datetime.now()
        await interaction.response.defer()
        if "min" in time.lower():
            then = now + timedelta(minutes=int(time.replace("min", "")))
        elif "h" in time.lower():
            then = now + timedelta(hours=int(time.replace("h", "")))
        elif "d" in time.lower():
            then = now + timedelta(days=int(time.replace("d", "")))
        elif "m" in time.lower():
            then = now + timedelta(weeks= 4 * int(time.replace("m", "")))
        elif "y" in time.lower():
            then = now + timedelta(weeks= 52 * int(time.replace("y", "")))
        else:
            split = time.split(".")
            d = split[0]
            m = split[1]
            y = split[2]
            then = datetime(int(y), int(m), int(d))
        iso = then.isoformat()
        data["reminders"][iso] = {}
        data["reminders"][iso]["msg"] = msg
        data["reminders"][iso]["user"] = str(interaction.user.id)
        with open("database.json", "w") as filee:
            json.dump(data, filee, indent=4)
        await interaction.followup.send("Reminder set!")

    @tasks.loop(minutes=1)
    async def check_reminders(self):
        print("Checking reminders...")
        data = self.bot.data
        now = datetime.now()
        for iso in data["reminders"]:
            then = datetime.fromisoformat(iso)
            if then <= now:
                msg = data["reminders"][iso]["msg"]
                user = await self.bot.fetch_user(int(data["reminders"][iso]["user"]))
                channel = await self.bot.fetch_channel(1487902536147931271)
                embed = discord.Embed(colour=Colour.purple(), title="Upcoming Birthdays")
                embed.add_field(name="", value=msg, inline=False)
                await channel.send(embed=embed)


    @check_reminders.before_loop
    async def before_check_reminders(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(ReminderCommand(bot))