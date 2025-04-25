import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
import logging

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="timeout", description="Timeout a user for a custom duration with a reason.")
    @app_commands.describe(
        user="The user to timeout",
        duration="The duration of the timeout in minutes",
        reason="The reason for the timeout"
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, user: discord.Member, duration: int, reason: str):
        timeout_duration = timedelta(minutes=duration)

        # Attempt to timeout the user
        try:
            await user.timeout(timeout_duration, reason=reason)
        except discord.Forbidden:
            await interaction.response.send_message(
                f"❌ I do not have permission to timeout {user.mention}.",
                ephemeral=True
            )
            return
        except discord.HTTPException as e:
            await interaction.response.send_message(
                f"❌ Failed to timeout {user.mention}. Error: {e}",
                ephemeral=True
            )
            return

        # Send a DM to the user
        try:
            dm_embed = discord.Embed(
                title="⏳ You Have Been Timed Out",
                description=f"You have been timed out in **{interaction.guild.name}**.",
                color=discord.Color.red()
            )
            dm_embed.add_field(name="Duration", value=f"{duration} minutes", inline=False)
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.set_footer(text="Please follow the server rules to avoid further actions.")
            await user.send(embed=dm_embed)
        except discord.Forbidden:
            await interaction.response.send_message(
                f"⚠️ Could not send a DM to {user.mention}. They might have DMs disabled.",
                ephemeral=True
            )

        # Notify the channel
        channel_embed = discord.Embed(
            title="✅ User Timed Out",
            description=f"{user.mention} has been timed out.",
            color=discord.Color.orange()
        )
        channel_embed.add_field(name="Duration", value=f"{duration} minutes", inline=False)
        channel_embed.add_field(name="Reason", value=reason, inline=False)
        channel_embed.set_footer(text=f"Timed out by {interaction.user}", icon_url=interaction.user.avatar.url)

        await interaction.response.send_message(embed=channel_embed)

        # Log the timeout action
        logging.info(f"⏳ {user} was timed out by {interaction.user} for {duration} minutes. Reason: {reason}")

async def setup(bot):
    await bot.add_cog(Moderation(bot))