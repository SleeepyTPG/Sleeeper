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
                description=f"You have been timed out in **{interaction.guild.name if interaction.guild else 'this server'}**.",
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
        avatar_url = interaction.user.avatar.url if interaction.user.avatar else None
        channel_embed.set_footer(text=f"Timed out by {interaction.user}", icon_url=avatar_url)

        await interaction.response.send_message(embed=channel_embed)

        logging.info(f"⏳ {user} was timed out by {interaction.user} for {duration} minutes. Reason: {reason}")

    @app_commands.command(name="lock_channel", description="Locks the current channel so no one can write.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def _lock_channel(self, interaction: discord.Interaction):
        channel = interaction.channel
        guild = interaction.guild

        if guild is None:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )
            return

        if isinstance(channel, discord.TextChannel):
            overwrite = channel.overwrites_for(guild.default_role)
            overwrite.send_messages = False
            await channel.set_permissions(guild.default_role, overwrite=overwrite)

            channel_display = getattr(channel, "mention", None) or getattr(channel, "name", str(channel))
            await interaction.response.send_message(
                f"🔒 The channel {channel_display} has been locked. Members can no longer write here."
            )
        else:
            await interaction.response.send_message(
                "❌ This command can only be used in a text channel.",
                ephemeral=True
            )

        if isinstance(channel, discord.TextChannel):
            overwrite = channel.overwrites_for(guild.default_role)
            overwrite.send_messages = True
            await channel.set_permissions(guild.default_role, overwrite=overwrite)

            await interaction.response.send_message(
                f"🔓 The channel {channel.mention} has been unlocked. Members can write here again."
            )
        else:
            await interaction.response.send_message(
                "❌ This command can only be used in a text channel.",
                ephemeral=True
            )
    
    @app_commands.command(name="warn", description="Warns a user and sends them a DM with the reason.")
    @app_commands.describe(user="The user to warn", reason="The reason for the warning")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def _warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )
            return

        warning_id = self.get_next_warn_id(interaction.guild)

        warns_add_user(user, interaction.guild, reason)

        dm_embed = discord.Embed(
            title="⚠️ You Have Been Warned",
            description=f"You have been warned in **{interaction.guild.name}**.",
            color=discord.Color.red()
        )
        dm_embed.add_field(name="Reason", value=reason, inline=False)
        dm_embed.add_field(name="Warning ID", value=f"`{warning_id}`", inline=False)
        avatar_url = interaction.user.avatar.url if interaction.user.avatar else None
        dm_embed.set_footer(text=f"Warned by {interaction.user}", icon_url=avatar_url)

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
        avatar_url = interaction.user.avatar.url if interaction.user.avatar else None
        channel_embed.set_footer(text=f"Warned by {interaction.user}", icon_url=avatar_url)

        await interaction.response.send_message(embed=channel_embed)

        if log_channel_id := warns_get_channel(interaction.guild):
            if log_channel := interaction.guild.get_channel(log_channel_id["channel"]):
                if isinstance(log_channel, discord.TextChannel):
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
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )
            return
        warns_set_channel(channel, interaction.guild)
        await interaction.response.send_message(
            f"✅ Warning log channel has been set to {channel.mention}.",
            ephemeral=True
        )

    @app_commands.command(name="clear", description="Delete a number of messages from the current channel.")
    @app_commands.describe(messages="The number of messages to delete (max 100)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, messages: int):
        if not isinstance(interaction.channel, discord.TextChannel):
            await interaction.response.send_message(
                "❌ This command can only be used in a text channel.",
                ephemeral=True
            )
            return

        if messages < 1 or messages > 100:
            await interaction.response.send_message(
                "❌ Please specify a number between 1 and 100.",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        deleted = await interaction.channel.purge(limit=messages)
        await interaction.followup.send(
            f"🧹 Deleted {len(deleted)} message(s) from {interaction.channel.mention}.",
            ephemeral=True
        )

    def get_next_warn_id(self, guild: discord.Guild) -> str:
        warns_increase_id(guild)
        result = warns_get_id(guild)
        if result is not None and 'id' in result:
            return f"{result['id']:04d}"
        else:
            return "0000"

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            perms = ', '.join(error.missing_permissions)
            await interaction.response.send_message(
                f"❌ You are missing the following permission(s) to use this command: **{perms}**.",
                ephemeral=True
            )
        elif isinstance(error, app_commands.errors.BotMissingPermissions):
            perms = ', '.join(error.missing_permissions)
            await interaction.response.send_message(
                f"❌ I am missing the following permission(s) to execute this command: **{perms}**.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ An unexpected error occurred while executing the command.",
                ephemeral=True
            )
            raise error

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
