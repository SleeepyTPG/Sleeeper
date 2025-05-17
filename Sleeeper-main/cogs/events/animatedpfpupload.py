import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import io

ALLOWED_USERS = {1104736921474834493}

class AnimatedPFP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setgifpfp", description="Upload a GIF to set as the bot's profile picture.")
    @app_commands.describe(gif="Attach a GIF file for the bot's profile picture.")
    async def setgifpfp(self, interaction: discord.Interaction, gif: discord.Attachment):
        if interaction.user.id not in ALLOWED_USERS:
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        if not gif.filename.lower().endswith(".gif"):
            await interaction.response.send_message("❌ Please upload a valid GIF file.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(gif.url) as resp:
                    if resp.status != 200:
                        await interaction.followup.send("❌ Failed to download the GIF.", ephemeral=True)
                        return
                    data = await resp.read()
            await self.bot.user.edit(avatar=data)
            await interaction.followup.send("✅ Bot profile picture updated successfully!", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.followup.send(f"❌ Failed to update profile picture: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AnimatedPFP(bot))