from discord.ext import commands, tasks
import json
import time

class BackupSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.create_backup.start()

    @tasks.loop(hours=1)
    async def create_backup(self):
        data = self.bot.data
        data["lastBackup"] = time.time()
        with open("database_backup.json", "w") as filee:
            json.dump(data, filee, indent=4)
        print("Backup saved!")

    @create_backup.before_loop
    async def before_check_birthdays(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(BackupSystem(bot))