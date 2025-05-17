import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import io

ALLOWED_USERS = {1104736921474834493}

class AnimatedPFP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setpfp", description="Upload a GIF, PNG, or JPG to set as the bot's profile picture.")
    @app_commands.describe(image="Attach a GIF, PNG, or JPG file for the bot's profile picture.")
    async def setpfp(self, interaction: discord.Interaction, image: discord.Attachment):
        if interaction.user.id not in ALLOWED_USERS:
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        valid_extensions = (".gif", ".png", ".jpg", ".jpeg")
        if not image.filename.lower().endswith(valid_extensions):
            await interaction.response.send_message("❌ Please upload a valid GIF, PNG, or JPG file.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image.url) as resp:
                    if resp.status != 200:
                        await interaction.followup.send("❌ Failed to download the image.", ephemeral=True)
                        return
                    data = await resp.read()
            await self.bot.user.edit(avatar=data)
            await interaction.followup.send("✅ Bot profile picture updated successfully!", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.followup.send(f"❌ Failed to update profile picture: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AnimatedPFP(bot))