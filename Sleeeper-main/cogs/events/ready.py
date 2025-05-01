import logging
from discord.ext import commands

logger = logging.getLogger(__name__)


class Ready(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener("on_ready")
    async def _on_ready(self):
        logger.info(f"🤖 Bot is Online as {self.bot.user}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Ready(bot))
