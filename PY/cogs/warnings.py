import discord
from discord.ext import commands
import uuid

WARNING_LOG_FILE = "warnings.log"

class Warnings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="warn", description="Warns a user and sends them a DM with the reason.")
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, user: discord.Member, *, reason: str):
        warning_id = str(uuid.uuid4())[:8]

        dm_embed = discord.Embed(
            title="⚠️ You Have Been Warned",
            description=f"You have been warned in **{ctx.guild.name}**.",
            color=discord.Color.red()
        )
        dm_embed.add_field(name="Reason", value=reason, inline=False)
        dm_embed.add_field(name="Warning ID", value=warning_id, inline=False)
        dm_embed.set_footer(text=f"Warned by {ctx.author}", icon_url=ctx.author.avatar.url)

        try:
            await user.send(embed=dm_embed)
        except discord.Forbidden:
            await ctx.send(f"❌ Could not send a DM to {user.mention}. They might have DMs disabled.")
            return

        channel_embed = discord.Embed(
            title="✅ User Warned",
            description=f"{user.mention} has been warned.",
            color=discord.Color.orange()
        )
        channel_embed.add_field(name="Reason", value=reason, inline=False)
        channel_embed.add_field(name="Warning ID", value=warning_id, inline=False)
        channel_embed.set_footer(text=f"Warned by {ctx.author}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=channel_embed)

        with open(WARNING_LOG_FILE, "a") as log_file:
            log_file.write(f"{warning_id} | {user} | {reason} | Warned by {ctx.author}\n")

async def setup(bot):
    await bot.add_cog(Warnings(bot))