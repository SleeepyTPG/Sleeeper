import os
import glob
import discord
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)


class Bot(commands.Bot):
    def __init__(self, cog_dir: str = "cogs"):
        super().__init__(
            command_prefix="´", 
            intents=discord.Intents.all(),
            help_command=None
        )

        self.cog_dir = cog_dir

    async def setup_hook(self):
        for file in self._find_cogs():
            await self.load_extension(file)
            logger.info(f"✅ Loaded cog: {file}")

        self.loop.create_task(self._sync_commands())

    async def _sync_commands(self):
        await self.tree.sync()
        logger.info("✅ Application commands synced with Discord.")

    def _find_cogs(self):
        files = glob.glob(f"{self.cog_dir}/**/*.py", recursive=True)
        files = [file[:-3] for file in files]
        files = [file.replace(os.path.sep, ".") for file in files]

        return files
