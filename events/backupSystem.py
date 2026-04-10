from discord.ext import commands
import json
import time

class BackupSystem(commands.Cog):
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
        if time.time() - data["lastBackup"] > 3600:
            data["lastBackup"] = time.time()
            with open("database_backup.json", "w") as filee:
                json.dump(data, filee, indent=4)
            print("Backup saved!")

async def setup(bot):
    await bot.add_cog(BackupSystem(bot))