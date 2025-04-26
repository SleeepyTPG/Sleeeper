import discord
from discord.ext import commands
from discord import app_commands
import random

marriages = {}

class Random(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="marry", description="Propose to another user!")
    @app_commands.describe(user="The user you want to marry")
    async def marry(self, interaction: discord.Interaction, user: discord.Member):
        if user == interaction.user:
            await interaction.response.send_message("💔 You can't marry yourself!", ephemeral=True)
            return

        if interaction.user.id in marriages:
            await interaction.response.send_message("💔 You are already married! Divorce first to marry someone else.", ephemeral=True)
            return

        if user.id in marriages:
            await interaction.response.send_message(f"💔 {user.mention} is already married to someone else!", ephemeral=True)
            return

        marriages[interaction.user.id] = user.id
        marriages[user.id] = interaction.user.id

        embed = discord.Embed(
            title="💍 Marriage Proposal",
            description=f"{interaction.user.mention} has proposed to {user.mention}! 💕\n\nThey are now married! 🎉",
            color=discord.Color.pink()
        )
        embed.set_footer(text="Congratulations on your marriage!")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="divorce", description="Divorce your current partner.")
    async def divorce(self, interaction: discord.Interaction):
        if interaction.user.id not in marriages:
            await interaction.response.send_message("💔 You are not married to anyone!", ephemeral=True)
            return

        partner_id = marriages.pop(interaction.user.id)
        marriages.pop(partner_id, None)

        partner = await self.bot.fetch_user(partner_id)

        embed = discord.Embed(
            title="💔 Divorce",
            description=f"{interaction.user.mention} has divorced {partner.mention}. 😢",
            color=discord.Color.red()
        )
        embed.set_footer(text="We hope you find happiness again.")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="roast", description="Generate a random roast message.")
    async def roast(self, interaction: discord.Interaction):
        roasts = [
            "You're like a cloud. When you disappear, it's a beautiful day.",
            "You're proof that even the worst mistakes can be fixed.",
            "You're like a software bug—annoying and hard to get rid of.",
            "You bring everyone so much joy… when you leave the room.",
            "You're like a Wi-Fi signal—weak and unreliable.",
            "You're the reason shampoo bottles have instructions.",
            "You're like a broken keyboard—completely useless.",
            "You're like a 404 error—nobody wants to see you.",
            "You're like a virus—nobody wants you around.",
            "You're like a pop-up ad—annoying and unnecessary."
        ]

        roast_message = random.choice(roasts)

        embed = discord.Embed(
            title="🔥 Roast Generator",
            description=f"{interaction.user.mention}, here's your roast:\n\n**{roast_message}**",
            color=discord.Color.orange()
        )
        embed.set_footer(text="Don't take it personally 😉")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Random(bot))