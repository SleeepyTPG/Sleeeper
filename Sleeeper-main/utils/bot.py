import os
import glob
import discord
from discord.ext import commands
import logging
import aiomysql

logger = logging.getLogger(__name__)


class Bot(commands.Bot):
    def __init__(self, cog_dir: str = "cogs"):
        super().__init__(
            command_prefix="´", 
            intents=discord.Intents.all()
        )

        self.cog_dir = cog_dir
        self.mysql_pool = None

    async def setup_hook(self):
        for file in self._find_cogs():
            await self.load_extension(file)
            logger.info(f"✅ Loaded cog: {file}")

        self.loop.create_task(self._sync_commands())

        self.mysql_pool = await aiomysql.create_pool(
            host="db0.fps.ms",
            port=3306,
            user="u61176_eKPaZTch0u",
            password="G34z!nAU=CO61bIrlOY9IxAY",
            db="s61176_sleeeper",
            autocommit=True
        )
        logger.info("MySQL pool created.")

    async def _sync_commands(self):
        await self.tree.sync()
        logger.info("✅ Application commands synced with Discord.")

    def _find_cogs(self):
        files = glob.glob(f"{self.cog_dir}/**/*.py", recursive=True)
        files = [file[:-3] for file in files]
        files = [file.replace(os.path.sep, ".") for file in files]

        return files


    async def get_mysql_pool(self):
        if self.mysql_pool is None:
            raise RuntimeError("MySQL pool not initialized!")
        return self.mysql_pool