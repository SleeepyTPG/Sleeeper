import discord
from discord.ext import commands
import json
import os

AFK_FILE = "afk_users.json"

def save_afk_users(afk_users):
    with open(AFK_FILE, "w") as file:
        json.dump(afk_users, file)

def load_afk_users():
    if os.path.exists(AFK_FILE):
        with open(AFK_FILE, "r") as file:
            return json.load(file)
    return {}

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afk_users = load_afk_users()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        # Notify users who mention an AFK user
        for user_id, reason in self.afk_users.items():
            if message.mentions and user_id in [mention.id for mention in message.mentions]:
                afk_user = await self.bot.fetch_user(user_id)

                afk_notify_embed = discord.Embed(
                    title="🚨 User is AFK",
                    description=f"{afk_user.mention} is currently AFK.",
                    color=discord.Color.orange()
                )
                afk_notify_embed.add_field(name="Reason", value=reason, inline=False)
                afk_notify_embed.set_footer(text="They will respond when they return.")

                await message.reply(embed=afk_notify_embed, mention_author=False)

        # Remove AFK status when the user sends a message
        if message.author.id in self.afk_users:
            del self.afk_users[message.author.id]
            save_afk_users(self.afk_users)

            afk_removed_embed = discord.Embed(
                title="✅ Welcome Back!",
                description=f"{message.author.mention}, your AFK status has been removed.",
                color=discord.Color.green()
            )
            afk_removed_embed.set_footer(text="Glad to have you back!")

            await message.channel.send(embed=afk_removed_embed, delete_after=10)

    @commands.command(name="afk", description="Set your AFK status with an optional reason.")
    async def afk(self, ctx, *, reason: str = "No reason provided"):
        self.afk_users[ctx.author.id] = reason
        save_afk_users(self.afk_users)

        afk_embed = discord.Embed(
            title="✅ AFK Status Set",
            description=f"{ctx.author.mention}, you are now AFK.",
            color=discord.Color.blue()
        )
        afk_embed.add_field(name="Reason", value=reason, inline=False)
        afk_embed.set_footer(text="You will be notified when someone mentions you.")

        await ctx.send(embed=afk_embed)

async def setup(bot):
    await bot.add_cog(AFK(bot))