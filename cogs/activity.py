import discord
from discord.ext import commands, tasks
import asyncio

class Activity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.activities = [
            discord.Activity(type=discord.ActivityType.watching, name="The final release of the bot"),
        ]
        self.activity_index = 0
        self.update_activity.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"🤖 Bot is Online as {self.bot.user}")

    @tasks.loop(seconds=30)
    async def update_activity(self):
        total_servers = len(self.bot.guilds)
        self.activities[0] = discord.Activity(type=discord.ActivityType.watching, name=f"over {total_servers} servers")

        self.activity_index = (self.activity_index + 1) % len(self.activities)
        await self.bot.change_presence(activity=self.activities[self.activity_index])

    @update_activity.before_loop
    async def before_update_activity(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Activity(bot))