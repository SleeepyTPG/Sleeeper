import discord
from discord.ext import commands
from discord import app_commands
from utils import logging_get_channel, logging_set_channel

ALLOWED_SERVERS = [1328784978309288087, 1245052473236783216, 1047234324296114256]


class ServerLogging(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def is_allowed_server(self, guild: discord.Guild):
        return guild.id in ALLOWED_SERVERS
    
    def get_log_channel(self, guild: discord.Guild):
        channel_id = logging_get_channel(guild)
        if channel_id:
            return self.bot.get_channel(channel_id.get("channel"))
        return None

    @commands.Cog.listener("on_member_ban")
    async def _on_member_ban(self, guild: discord.Guild, user: discord.User):
        if not self.is_allowed_server(guild):
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

    @commands.Cog.listener("on_member_remove")
    async def _on_member_remove(self, member: discord.Member):
        if not self.is_allowed_server(member.guild):
            return
        log_channel = self.get_log_channel(member.guild)
        if log_channel:
            embed = discord.Embed(
                title="🚪 Member Left or Kicked",
                description=f"{member.mention} ({member}) has left or was kicked.",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"User ID: {member.id}")
            await log_channel.send(embed=embed)

    @commands.Cog.listener("on_member_update")
    async def _on_member_update(self, before: discord.Member, after: discord.Member):
        if not self.is_allowed_server(before.guild):
            return
        
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

    @commands.Cog.listener("on_message_delete")
    async def _on_message_delete(self, message: discord.Message):
        if not self.is_allowed_server(message.guild) or message.author.bot:
            return
        
        log_channel = self.get_log_channel(message.guild)
        if log_channel:
            embed = discord.Embed(
                title="🗑️ Message Deleted",
                description=f"Message by {message.author.mention} was deleted in {message.channel.mention}.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Content", value=message.content or "No content", inline=False)
            embed.set_footer(text=f"User ID: {message.author.id}")
            await log_channel.send(embed=embed)

    @commands.Cog.listener("on_message_edit")
    async def _on_message_edit(self, before: discord.Message, after: discord.Message):
        if not self.is_allowed_server(before.guild) or before.author.bot or before.content == after.content:
            return
        
        log_channel = self.get_log_channel(before.guild)
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

    @app_commands.command(name="set_log_channel", description="Set the channel where logs will be sent.")
    @app_commands.describe(channel="The channel to send logs")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not self.is_allowed_server(interaction.guild):
            await interaction.response.send_message("❌ This server is not authorized to use logging.", ephemeral=True)
            return
        
        logging_set_channel(channel, interaction.guild)
        await interaction.response.send_message(f"✅ Logs will now be sent in {channel.mention}.")


async def setup(bot: commands.Bot):
    await bot.add_cog(ServerLogging(bot))
