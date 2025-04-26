import discord
from discord.ext import commands
from discord import app_commands

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

async def setup(bot):
    await bot.add_cog(Random(bot))