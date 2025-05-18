import discord
from discord.ext import commands
from discord import app_commands
from utils import logging_get_channel, logging_set_channel

class ServerLogging(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_log_channel(self, guild: discord.Guild) -> discord.TextChannel | None:
        channel_id = logging_get_channel(guild)
        if channel_id:
            channel_value = channel_id.get("channel")
            if isinstance(channel_value, int):
                channel = self.bot.get_channel(channel_value)
                if isinstance(channel, discord.TextChannel):
                    return channel
        return None

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        log_channel = self.get_log_channel(guild)
        if log_channel:
            embed = discord.Embed(
                title="🔨 Member Banned",
                description=f"{user.mention} ({user}) was banned.",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"User ID: {user.id}")
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        log_channel = self.get_log_channel(member.guild)
        if log_channel:
            embed = discord.Embed(
                title="🚪 Member Left or Kicked",
                description=f"{member.mention} ({member}) has left or was kicked.",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"User ID: {member.id}")
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        log_channel = self.get_log_channel(before.guild)
        if before.display_name != after.display_name:
            if log_channel:
                embed = discord.Embed(
                    title="✏️ Nickname Changed",
                    description=f"{before.mention} changed their nickname.",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Before", value=before.display_name, inline=True)
                embed.add_field(name="After", value=after.display_name, inline=True)
                embed.set_footer(text=f"User ID: {before.id}")
                await log_channel.send(embed=embed)

        if before.timed_out_until != after.timed_out_until:
            if log_channel:
                embed = discord.Embed(
                    title="⏳ Member Timeout Updated",
                    description=f"{before.mention}'s timeout status was updated.",
                    color=discord.Color.purple()
                )
                embed.add_field(name="Before", value=str(before.timed_out_until), inline=True)
                embed.add_field(name="After", value=str(after.timed_out_until), inline=True)
                embed.set_footer(text=f"User ID: {before.id}")
                await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return

        log_channel = self.get_log_channel(message.guild)
        if log_channel:
            if isinstance(message.channel, discord.TextChannel):
                channel_mention = message.channel.mention
            elif hasattr(message.channel, "name"):
                channel_mention = f"#{getattr(message.channel, 'name', 'unknown')}"
            else:
                channel_mention = str(message.channel)
            embed = discord.Embed(
                title="🗑️ Message Deleted",
                description=f"Message by {message.author.mention} was deleted in {channel_mention}.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Content", value=message.content or "No content", inline=False)
            embed.set_footer(text=f"User ID: {message.author.id}")
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if not before.guild or before.author.bot or before.content == after.content:
            return

        log_channel = self.get_log_channel(before.guild)
        if log_channel:
            if isinstance(before.channel, discord.TextChannel):
                channel_mention = before.channel.mention
            elif isinstance(before.channel, discord.DMChannel):
                channel_mention = "Direct Message"
            elif isinstance(before.channel, discord.GroupChannel):
                channel_mention = f"Group: {getattr(before.channel, 'name', 'Unnamed Group')}"
            elif hasattr(before.channel, "name"):
                channel_mention = f"#{getattr(before.channel, 'name', 'unknown')}"
            else:
                channel_mention = str(before.channel)
            embed = discord.Embed(
                title="✏️ Message Edited",
                description=f"Message by {before.author.mention} was edited in {channel_mention}.",
                color=discord.Color.yellow()
            )
            embed.add_field(name="Before", value=before.content or "No content", inline=False)
            embed.add_field(name="After", value=after.content or "No content", inline=False)
            embed.set_footer(text=f"User ID: {before.author.id}")
            await log_channel.send(embed=embed)

    @app_commands.command(name="set_log_channel", description="Set the channel where logs will be sent.")
    @app_commands.describe(channel="The channel to send logs")
    @app_commands.checks.has_permissions(administrator=True)
    async def _set_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if interaction.guild is None:
            await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
            return
        logging_set_channel(channel, interaction.guild)
        await interaction.response.send_message(f"✅ Logs will now be sent in {channel.mention}.")

async def setup(bot: commands.Bot):
    await bot.add_cog(ServerLogging(bot))
