import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="´", intents=discord.Intents.all())

    async def setup_hook(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")
                logging.info(f"✅ Loaded cog: {filename[:-3]}")

        await self.tree.sync()
        logging.info("✅ Application commands synced with Discord.")

bot = MyBot()

@bot.event
async def on_ready():
    logging.info(f"🤖 Bot is Online as {bot.user}")

bot.run(os.getenv("DISCORD_BOT_TOKEN"))