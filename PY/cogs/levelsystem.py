import discord
from discord.ext import commands
from discord import app_commands
import json
import os

LEVELS_FILE = "levels.json"
LEVEL_CHANNELS_FILE = "level_channels.json"

def load_levels():
    if os.path.exists(LEVELS_FILE):
        with open(LEVELS_FILE, "r") as file:
            return json.load(file)
    return {}

def save_levels(levels):
    with open(LEVELS_FILE, "w") as file:
        json.dump(levels, file)

def load_level_channels():
    if os.path.exists(LEVEL_CHANNELS_FILE):
        with open(LEVEL_CHANNELS_FILE, "r") as file:
            return json.load(file)
    return {}

def save_level_channels(level_channels):
    with open(LEVEL_CHANNELS_FILE, "w") as file:
        json.dump(level_channels, file)

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.levels = load_levels()
        self.level_channels = load_level_channels()

    def _add_xp(self, user_id: int, guild_id: int, xp: int):
        if str(guild_id) not in self.levels:
            self.levels[str(guild_id)] = {}

        if str(user_id) not in self.levels[str(guild_id)]:
            self.levels[str(guild_id)][str(user_id)] = {"xp": 0, "level": 1}

        user_data = self.levels[str(guild_id)][str(user_id)]
        user_data["xp"] += xp

        next_level_xp = user_data["level"] * 100

        if user_data["xp"] >= next_level_xp:
            user_data["level"] += 1
            user_data["xp"] -= next_level_xp
            save_levels(self.levels)
            return True, user_data["level"]
        else:
            save_levels(self.levels)
            return False, user_data["level"]

    def get_user_data(self, user_id: int, guild_id: int):
        """Retrieve a user's level and XP data for a specific server."""
        if str(guild_id) in self.levels and str(user_id) in self.levels[str(guild_id)]:
            return self.levels[str(guild_id)][str(user_id)]
        return {"xp": 0, "level": 1}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        leveled_up, new_level = self._add_xp(message.author.id, message.guild.id, xp=10)

        if leveled_up:
            embed = discord.Embed(
                title="🎉 Level Up!",
                description=f"Congratulations {message.author.mention}, you reached **Level {new_level}**!",
                color=discord.Color.green()
            )
            embed.set_footer(text="Keep chatting to level up more!")

            guild_id = str(message.guild.id)
            if guild_id in self.level_channels:
                level_channel_id = self.level_channels[guild_id]
                level_channel = self.bot.get_channel(level_channel_id)
                if level_channel:
                    await level_channel.send(embed=embed)
                    return

            await message.channel.send(embed=embed)

    @app_commands.command(name="rank", description="Check your current level and XP.")
    async def rank(self, interaction: discord.Interaction):
        user_data = self.get_user_data(interaction.user.id, interaction.guild.id)
        embed = discord.Embed(
            title=f"📊 {interaction.user.display_name}'s Rank",
            description=f"**Level:** {user_data['level']}\n**XP:** {user_data['xp']}/{user_data['level'] * 100}",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Keep chatting to earn more XP!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="Show the server's top users by level.")
    async def leaderboard(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        if guild_id not in self.levels:
            await interaction.response.send_message("No data available for this server.", ephemeral=True)
            return

        leaderboard = sorted(
            self.levels[guild_id].items(),
            key=lambda x: (x[1]["level"], x[1]["xp"]),
            reverse=True
        )

        embed = discord.Embed(
            title="🏆 Server Leaderboard",
            color=discord.Color.gold()
        )

        for i, (user_id, data) in enumerate(leaderboard[:10], start=1):
            user = await self.bot.fetch_user(int(user_id))
            embed.add_field(
                name=f"{i}. {user.display_name}",
                value=f"**Level:** {data['level']} | **XP:** {data['xp']}",
                inline=False
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="set_level_channel", description="Set the channel where level-up messages will be sent.")
    @app_commands.describe(channel="The channel to send level-up messages")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_level_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Set the level-up notification channel for the server."""
        self.level_channels[str(interaction.guild.id)] = channel.id
        save_level_channels(self.level_channels)
        await interaction.response.send_message(f"✅ Level-up messages will now be sent in {channel.mention}.")

async def setup(bot):
    await bot.add_cog(LevelSystem(bot))