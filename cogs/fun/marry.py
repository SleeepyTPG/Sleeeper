import discord
from discord.ext import commands
from discord import app_commands
from utils import marry_add_user, marry_get_user, marry_remove_user


class ProposalView(discord.ui.View):
    def __init__(self, proposer: discord.Member, proposee: discord.Member):
        super().__init__(timeout=360)
        self.proposer = proposer
        self.proposee = proposee
        self.result = None

    @discord.ui.button(label="Accept 💍", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.proposee:
            await interaction.response.send_message("❌ This proposal is not for you!", ephemeral=True)
            return

        marry_add_user(self.proposer, self.proposee)

        embed = discord.Embed(
            title="💍 Marriage Accepted!",
            description=f"{self.proposee.mention} has accepted {self.proposer.mention}'s proposal! 🎉",
            color=discord.Color.green()
        )
        embed.set_footer(text="Congratulations on your marriage!")
        await interaction.response.edit_message(embed=embed, view=None)
        self.result = "accepted"
        self.stop()

    @discord.ui.button(label="Decline 💔", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.proposee:
            await interaction.response.send_message("❌ This proposal is not for you!", ephemeral=True)
            return

        embed = discord.Embed(
            title="💔 Proposal Declined",
            description=f"{self.proposee.mention} has declined {self.proposer.mention}'s proposal. 😢",
            color=discord.Color.red()
        )
        embed.set_footer(text="Better luck next time!")
        await interaction.response.edit_message(embed=embed, view=None)
        self.result = "declined"
        self.stop()


class Marry(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="marry", description="Propose to another user!")
    @app_commands.describe(user="The user you want to marry")
    async def marry(self, interaction: discord.Interaction, user: discord.Member):
        if not interaction.guild:
            return await interaction.response.send_message("This is a guild only command!", ephemeral=True)

        if user.id == interaction.user.id:
            return await interaction.response.send_message("💔 You can't marry yourself!", ephemeral=True)
        
        if user.bot:   
            return await interaction.response.send_message("💔 You can't marry a bot!", ephemeral=True)
        
        self_married = marry_get_user(interaction.user)
        other_married = marry_get_user(user)

        if self_married:
            await interaction.response.send_message("💔 You are already married! Divorce first to marry someone else.", ephemeral=True)
            return

        if other_married:
            await interaction.response.send_message(f"💔 {user.mention} is already married to someone else!", ephemeral=True)
            return

        embed = discord.Embed(
            title="💍 Marriage Proposal",
            description=f"{interaction.user.mention} has proposed to {user.mention}! 💕\n\n{user.mention}, do you accept?",
            color=discord.Color.pink()
        )
        embed.set_footer(text="You have 6 Minutes to respond.")

        view = ProposalView(proposer=interaction.user, proposee=user)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="divorce", description="Divorce your current partner.")
    async def divorce(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message("This is a guild only command!", ephemeral=True)

        if not marry_get_user(interaction.user):
            await interaction.response.send_message("💔 You are not married to anyone!", ephemeral=True)
            return

        result = marry_remove_user(interaction.user)

        partner_id = result["member1"] if result["member1"] != interaction.user.id else result["member2"]

        embed = discord.Embed(
            title="💔 Divorce",
            description=f"{interaction.user.mention} has divorced {partner_id}. 😢",
            color=discord.Color.red()
        )
        embed.set_footer(text="We hope you find happiness again.")

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Marry(bot))
