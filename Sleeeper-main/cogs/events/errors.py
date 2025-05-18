import discord
from discord.ext import commands
from discord import app_commands
import traceback
import sys

ERROR_GUILD_ID = 1245052473236783216
ERROR_CHANNEL_ID = 1372651387040698409
ERROR_ROLE_ID = 1267882950855364678

class ErrorLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_error(self, event_method, *args, **kwargs):
        tb = traceback.format_exc()
        channel = self.bot.get_channel(ERROR_CHANNEL_ID)
        guild = self.bot.get_guild(ERROR_GUILD_ID)
        guild_info = f"**Server:** {guild.name} (ID: {guild.id})\n**Members:** {guild.member_count}" if guild else "Server info not found."
        tb_list = traceback.extract_tb(sys.exc_info()[2])
        if tb_list:
            last_frame = tb_list[-1]
            file_info = f"**File:** `{last_frame.filename}`\n**Line:** `{last_frame.lineno}`\n**Function:** `{last_frame.name}`"
        else:
            file_info = "File info not found."

        if channel is not None:
            tb_short = tb[-1900:] if len(tb) > 1900 else tb
            embed = discord.Embed(
                title="⚠️ Bot Error",
                description=f"{guild_info}\n{file_info}\n\n**Event:** `{event_method}`\n```py\n{tb_short}\n```",
                color=discord.Color.red()
            )
            try:
                await channel.send(content=f"<@&{ERROR_ROLE_ID}>", embed=embed)
            except Exception as e:
                print("Failed to send error embed:", e)
        else:
            print("Error channel not found! Check ERROR_CHANNEL_ID and bot permissions.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        channel = self.bot.get_channel(ERROR_CHANNEL_ID)
        guild = ctx.guild
        guild_info = f"**Server:** {guild.name} (ID: {guild.id})\n**Members:** {guild.member_count}" if guild else "Server info not found."

        tb_list = traceback.extract_tb(error.__traceback__)
        if tb_list:
            last_frame = tb_list[-1]
            file_info = f"**File:** `{last_frame.filename}`\n**Line:** `{last_frame.lineno}`\n**Function:** `{last_frame.name}`"
        else:
            file_info = "File info not found."

        if channel is not None:
            tb_short = tb[-1900:] if len(tb) > 1900 else tb
            embed = discord.Embed(
                title="⚠️ Command Error",
                description=f"{guild_info}\n{file_info}\n\n**Command:** `{ctx.command}`\n```py\n{tb_short}\n```",
                color=discord.Color.red()
            )
            try:
                await channel.send(content=f"<@&{ERROR_ROLE_ID}>", embed=embed)
            except Exception as e:
                print("Failed to send command error embed:", e)
        else:
            print("Error channel not found! Check ERROR_CHANNEL_ID and bot permissions.")

    @commands.Cog.listener()
    async def on_application_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        channel = self.bot.get_channel(ERROR_CHANNEL_ID)
        guild = interaction.guild
        guild_info = f"**Server:** {guild.name} (ID: {guild.id})\n**Members:** {guild.member_count}" if guild else "Server info not found."

        tb_list = traceback.extract_tb(error.__traceback__)
        if tb_list:
            last_frame = tb_list[-1]
            file_info = f"**File:** `{last_frame.filename}`\n**Line:** `{last_frame.lineno}`\n**Function:** `{last_frame.name}`"
        else:
            file_info = "File info not found."

        if channel is not None:
            tb_short = tb[-1900:] if len(tb) > 1900 else tb
            embed = discord.Embed(
                title="⚠️ Slash Command Error",
                description=f"{guild_info}\n{file_info}\n\n**Command:** `{interaction.command}`\n```py\n{tb_short}\n```",
                color=discord.Color.red()
            )
            try:
                await channel.send(content=f"<@&{ERROR_ROLE_ID}>", embed=embed)
            except Exception as e:
                print("Failed to send slash command error embed:", e)
        else:
            print("Error channel not found! Check ERROR_CHANNEL_ID and bot permissions.")
    
    @app_commands.command(name="error", description="Test the error logger.")
    async def error_test(self, interaction: discord.Interaction):
        await interaction.response.send_message("This is a test error.")
        raise Exception("This is a test exception.")

async def setup(bot):
    await bot.add_cog(ErrorLogger(bot))