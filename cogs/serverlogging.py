import discord
from discord.ext import commands
from discord import app_commands
import json
import os

LOG_CHANNELS_FILE = "log_channels.json"

ALLOWED_SERVERS = [1328784978309288087, 1245052473236783216]

def load_log_channels():
    if os.path.exists(LOG_CHANNELS_FILE):
        with open(LOG_CHANNELS_FILE, "r") as file:
            return json.load(file)
    return {}

def save_log_channels(log_channels):
    with open(LOG_CHANNELS_FILE, "w") as file:
        json.dump(log_channels, file)

class ServerLogging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channels = load_log_channels()

    def is_allowed_server(self, guild_id):
        return guild_id in ALLOWED_SERVERS

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        if not self.is_allowed_server(guild.id):
            return
        log_channel = self.get_log_channel(guild.id)
        if log_channel:
            embed = discord.Embed(
                title="🔨 Member Banned",
                description=f"{user.mention} ({user}) was banned.",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"User ID: {user.id}")
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if not self.is_allowed_server(before.guild.id):
            return
        if before.display_name != after.display_name:
            log_channel = self.get_log_channel(before.guild.id)
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

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not self.is_allowed_server(message.guild.id) or message.author.bot:
            return
        log_channel = self.get_log_channel(message.guild.id)
        if log_channel:
            embed = discord.Embed(
                title="🗑️ Message Deleted",
                description=f"Message by {message.author.mention} was deleted in {message.channel.mention}.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Content", value=message.content or "No content", inline=False)
            embed.set_footer(text=f"User ID: {message.author.id}")
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not self.is_allowed_server(before.guild.id) or before.author.bot or before.content == after.content:
            return
        log_channel = self.get_log_channel(before.guild.id)
        if log_channel:
            embed = discord.Embed(
                title="✏️ Message Edited",
                description=f"Message by {before.author.mention} was edited in {before.channel.mention}.",
                color=discord.Color.yellow()
            )
            embed.add_field(name="Before", value=before.content or "No content", inline=False)
            embed.add_field(name="After", value=after.content or "No content", inline=False)
            embed.set_footer(text=f"User ID: {before.author.id}")
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if not self.is_allowed_server(member.guild.id):
            return
        log_channel = self.get_log_channel(member.guild.id)
        if log_channel:
            embed = discord.Embed(
                title="🚪 Member Left or Kicked",
                description=f"{member.mention} ({member}) has left or was kicked.",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"User ID: {member.id}")
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if not self.is_allowed_server(before.guild.id):
            return
        if before.timed_out_until != after.timed_out_until:
            log_channel = self.get_log_channel(before.guild.id)
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

    def get_log_channel(self, guild_id):
        channel_id = self.log_channels.get(str(guild_id))
        if channel_id:
            return self.bot.get_channel(channel_id)
        return None

    @app_commands.command(name="set_log_channel", description="Set the channel where logs will be sent.")
    @app_commands.describe(channel="The channel to send logs")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not self.is_allowed_server(interaction.guild.id):
            await interaction.response.send_message("❌ This server is not authorized to use logging.", ephemeral=True)
            return
        self.log_channels[str(interaction.guild.id)] = channel.id
        save_log_channels(self.log_channels)
        await interaction.response.send_message(f"✅ Logs will now be sent in {channel.mention}.")

async def setup(bot):
    await bot.add_cog(ServerLogging(bot))