import time
import discord
from discord.ext import commands
from discord import app_commands
from utils import afk_remove_user, afk_get_user, afk_add_user


class AFK(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild:
            return

        if message.author.bot:
            return

        if user := afk_get_user(message.author, message.guild):
            if message.mentions and user["member"] in [mention.id for mention in message.mentions]:
                afk_notify_embed = discord.Embed(
                    title="🚨 User is AFK",
                    description=f"<@{user['member']}> is AFK since <t:{user['since']}:R>.",
                    color=discord.Color.orange()
                )
                afk_notify_embed.add_field(name="Reason", value=user["reason"], inline=False)
                afk_notify_embed.set_footer(text="They will respond when they return.")

                await message.reply(embed=afk_notify_embed, delete_after=10)

            if message.author.id == user["member"]:
                afk_remove_user(message.author, message.guild)

                afk_removed_embed = discord.Embed(
                    title="✅ Welcome Back!",
                    description=f"{message.author.mention}, you have been AFK since <t:{user['since']}:R>.",
                    color=discord.Color.green()
                )
                afk_removed_embed.set_footer(text="Glad to have you back!")

                await message.channel.send(embed=afk_removed_embed, delete_after=10)

    @app_commands.command(name="afk", description="Set your AFK status with an optional reason.")
    @app_commands.describe(reason="The reason for going AFK")
    async def afk(self, interaction: discord.Interaction, reason: str = "No reason provided"):
        """Set the user's AFK status."""
        if not interaction.guild:
            return await interaction.response.send_message("This is a guild only command.", ephemeral=True)

        if afk_get_user(interaction.user, interaction.guild):
            return await interaction.response.send_message("Your already set as afk.", ephemeral=True)

        afk_add_user(interaction.user, interaction.guild, reason)

        afk_embed = discord.Embed(
            title="✅ AFK Status Set",
            description=f"{interaction.user.mention}, you are now AFK.",
            color=discord.Color.blue()
        )
        afk_embed.add_field(name="Reason", value=reason, inline=False)
        afk_embed.set_footer(text="You will be notified when someone mentions you.")

        await interaction.response.send_message(embed=afk_embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(AFK(bot))
