import discord
from discord.ext import commands
import asyncio

CURRENT_VERSION = "0.9.2 Beta Build"

class Activity(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.activities = [
            discord.Activity(type=discord.ActivityType.watching, name=f"over 0 servers"),
            discord.Activity(type=discord.ActivityType.playing, name=f"Version {CURRENT_VERSION}")
        ]

    @commands.Cog.listener("on_ready")
    async def _on_ready(self):
        self.bot.loop.create_task(self._activity_loop())

    async def _activity_loop(self):
        while not self.bot.is_closed():
            total_servers = len(self.bot.guilds)
            self.activities[0].name = f"over {total_servers} servers"

            for activity in self.activities:
                await self.bot.change_presence(activity=activity)
                await asyncio.sleep(10)


async def setup(bot: commands.Bot):
    await bot.add_cog(Activity(bot))
