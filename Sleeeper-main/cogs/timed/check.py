import discord
from discord.ext import commands

CHANNEL_IDS = [1364860863558844416, 1362441210479775974]

class OnlineNotifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_online_message(self):
        await self.bot.wait_until_ready()
        for channel_id in CHANNEL_IDS:
            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.send("The bot is back online 🎉 | <@1104736921474834493>")

    @commands.Cog.listener()
    async def on_ready(self):
        await self.send_online_message()

async def setup(bot):
    await bot.add_cog(OnlineNotifier(bot))