import discord
from discord.ext import commands

class Activity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        total_members = sum(guild.member_count or 0 for guild in self.bot.guilds)
        await self.bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{total_members} Members"
        ))
        print(f"🤖 Bot is Online as {self.bot.user}")

async def setup(bot):
    await bot.add_cog(Activity(bot))