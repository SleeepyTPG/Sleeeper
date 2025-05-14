import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
import logging
from utils import warns_set_channel, warns_add_user, warns_get_channel, warns_get_user, warns_increase_id, warns_get_id


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="timeout", description="Timeout a user for a custom duration with a reason.")
    @app_commands.describe(
        user="The user to timeout",
        duration="The duration of the timeout in minutes",
        reason="The reason for the timeout"
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def _timeout(self, interaction: discord.Interaction, user: discord.Member, duration: int, reason: str):
        timeout_duration = timedelta(minutes=duration)

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

        channel_embed = discord.Embed(
            title="✅ User Timed Out",
            description=f"{user.mention} has been timed out.",
            color=discord.Color.orange()
        )
        channel_embed.add_field(name="Duration", value=f"{duration} minutes", inline=False)
        channel_embed.add_field(name="Reason", value=reason, inline=False)
        channel_embed.set_footer(text=f"Timed out by {interaction.user}", icon_url=interaction.user.avatar.url)

        await interaction.response.send_message(embed=channel_embed)

        logging.info(f"⏳ {user} was timed out by {interaction.user} for {duration} minutes. Reason: {reason}")

    @app_commands.command(name="lock_channel", description="Locks the current channel so no one can write.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def _lock_channel(self, interaction: discord.Interaction):
        channel = interaction.channel
        guild = interaction.guild

        overwrite = channel.overwrites_for(guild.default_role)
        overwrite.send_messages = False
        await channel.set_permissions(guild.default_role, overwrite=overwrite)

        await interaction.response.send_message(
            f"🔒 The channel {channel.mention} has been locked. Members can no longer write here."
        )

    @app_commands.command(name="unlock_channel", description="Unlocks the current channel so members can write again.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def _unlock_channel(self, interaction: discord.Interaction):
        channel = interaction.channel
        guild = interaction.guild

        overwrite = channel.overwrites_for(guild.default_role)
        overwrite.send_messages = True
        await channel.set_permissions(guild.default_role, overwrite=overwrite)

        await interaction.response.send_message(
            f"🔓 The channel {channel.mention} has been unlocked. Members can write here again."
        )
    
    @app_commands.command(name="warn", description="Warns a user and sends them a DM with the reason.")
    @app_commands.describe(user="The user to warn", reason="The reason for the warning")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def _warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        warning_id = self.get_next_warn_id(interaction.guild)

        warns_add_user(user, interaction.guild, reason)

        dm_embed = discord.Embed(
            title="⚠️ You Have Been Warned",
            description=f"You have been warned in **{interaction.guild.name}**.",
            color=discord.Color.red()
        )
        dm_embed.add_field(name="Reason", value=reason, inline=False)
        dm_embed.add_field(name="Warning ID", value=f"`{warning_id}`", inline=False)
        dm_embed.set_footer(text=f"Warned by {interaction.user}", icon_url=interaction.user.avatar.url)

        try:
            await user.send(embed=dm_embed)
        except discord.Forbidden:
            await interaction.response.send_message(
                f"❌ Could not send a DM to {user.mention}. They might have DMs disabled.",
                ephemeral=True
            )
            return

        channel_embed = discord.Embed(
            title="✅ User Warned",
            description=f"{user.mention} has been warned.",
            color=discord.Color.orange()
        )
        channel_embed.add_field(name="Reason", value=reason, inline=False)
        channel_embed.add_field(name="Warning ID", value=f"`{warning_id}`", inline=False)
        channel_embed.set_footer(text=f"Warned by {interaction.user}", icon_url=interaction.user.avatar.url)

        await interaction.response.send_message(embed=channel_embed)

        if log_channel_id := warns_get_channel(interaction.guild):
            if log_channel := interaction.guild.get_channel(log_channel_id["channel"]):
                log_embed = discord.Embed(
                    title="⚠️ Warning Logged",
                    description=f"A warning has been issued in **{interaction.guild.name}**.",
                    color=discord.Color.yellow()
                )
                log_embed.add_field(name="Warned User", value=user.mention, inline=False)
                log_embed.add_field(name="Reason", value=reason, inline=False)
                log_embed.add_field(name="Warning ID", value=f"`{warning_id}`", inline=False)
                log_embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
                log_embed.set_footer(text="Warning Log")
                await log_channel.send(embed=log_embed)

    @app_commands.command(name="set_warn_log", description="Set the channel where warnings will be logged.")
    @app_commands.describe(channel="The channel to log warnings")
    @app_commands.checks.has_permissions(administrator=True)
    async def _set_warn_log(self, interaction: discord.Interaction, channel: discord.TextChannel):
        warns_set_channel(channel, interaction.guild)
        await interaction.response.send_message(
            f"✅ Warning log channel has been set to {channel.mention}.",
            ephemeral=True
        )

    def get_next_warn_id(self, guild: discord.Guild) -> str:
        warns_increase_id(guild)
        result = warns_get_id(guild)
        return f"{result['id']:04d}"


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
