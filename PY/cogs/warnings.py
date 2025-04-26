import discord
from discord.ext import commands
from discord import app_commands
import random

log_channels = {}

class Warnings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="warn", description="Warns a user and sends them a DM with the reason.")
    @app_commands.describe(user="The user to warn", reason="The reason for the warning")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        warning_id = random.randint(1000, 9999)

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

        guild_id = interaction.guild.id
        if guild_id in log_channels:
            log_channel_id = log_channels[guild_id]
            log_channel = interaction.guild.get_channel(log_channel_id)
            if log_channel:
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
    async def set_warn_log(self, interaction: discord.Interaction, channel: discord.TextChannel):
        log_channels[interaction.guild.id] = channel.id
        await interaction.response.send_message(
            f"✅ Warning log channel has been set to {channel.mention}.",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Warnings(bot))