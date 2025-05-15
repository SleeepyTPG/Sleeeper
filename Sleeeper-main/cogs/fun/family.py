import discord
from discord.ext import commands
from discord import app_commands
from utils import marry_add_user, marry_get_user, marry_remove_user, adopt_user, get_adoption_data, remove_adoption


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


class AdoptionView(discord.ui.View):
    def __init__(self, adopter: discord.Member, adoptee: discord.Member):
        super().__init__(timeout=360)
        self.adopter = adopter
        self.adoptee = adoptee
        self.result = None

    @discord.ui.button(label="Accept 👪", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.adoptee:
            await interaction.response.send_message("❌ This adoption request is not for you!", ephemeral=True)
            return

        adopt_user(self.adopter, self.adoptee)

        embed = discord.Embed(
            title="👪 Adoption Accepted!",
            description=f"{self.adoptee.mention} has been adopted by {self.adopter.mention}! 🎉",
            color=discord.Color.green()
        )
        embed.set_footer(text="Congratulations on your new family!")
        await interaction.response.edit_message(embed=embed, view=None)
        self.result = "accepted"
        self.stop()

    @discord.ui.button(label="Decline 💔", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.adoptee:
            await interaction.response.send_message("❌ This adoption request is not for you!", ephemeral=True)
            return

        embed = discord.Embed(
            title="💔 Adoption Declined",
            description=f"{self.adoptee.mention} has declined {self.adopter.mention}'s adoption request. 😢",
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
    async def _marry(self, interaction: discord.Interaction, user: discord.Member):
        if not interaction.guild:
            return await interaction.response.send_message("This is a guild only command!", ephemeral=True)

        if user.id == interaction.user.id:
            return await interaction.response.send_message("💔 You can't marry yourself!", ephemeral=True)
        
        if user.bot:   
            return await interaction.response.send_message("💔 You can't marry a bot!", ephemeral=True)
        
        member = interaction.user
        if not isinstance(member, discord.Member):
            member = interaction.guild.get_member(member.id)
        if member is None:
            await interaction.response.send_message("❌ Could not find your member data in this guild.", ephemeral=True)
            return
        self_married = marry_get_user(member)
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

        proposer_member = interaction.user
        if not isinstance(proposer_member, discord.Member):
            proposer_member = interaction.guild.get_member(proposer_member.id)
        if proposer_member is None:
            await interaction.response.send_message("❌ Could not find your member data in this guild.", ephemeral=True)
            return
        view = ProposalView(proposer=proposer_member, proposee=user)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="divorce", description="Divorce your current partner.")
    async def _divorce(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message("This is a guild only command!", ephemeral=True)

        member = interaction.user
        if not isinstance(member, discord.Member):
            member = interaction.guild.get_member(member.id)
        if member is None:
            await interaction.response.send_message("❌ Could not find your member data in this guild.", ephemeral=True)
            return
        if not marry_get_user(member):
            await interaction.response.send_message("💔 You are not married to anyone!", ephemeral=True)
            return

        result = marry_remove_user(member)

        if not result:
            await interaction.response.send_message("❌ Failed to process your divorce. Please try again.", ephemeral=True)
            return

        partner_id = result["member1"] if result["member1"] != interaction.user.id else result["member2"]

        embed = discord.Embed(
            title="💔 Divorce",
            description=f"{interaction.user.mention} has divorced <@{partner_id}>. 😢",
            color=discord.Color.red()
        )
        embed.set_footer(text="We hope you find happiness again.")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="adopt", description="Adopt another user!")
    @app_commands.describe(user="The user you want to adopt")
    async def _adopt(self, interaction: discord.Interaction, user: discord.Member):
        if not interaction.guild:
            return await interaction.response.send_message("This is a guild-only command!", ephemeral=True)

        if user.id == interaction.user.id:
            return await interaction.response.send_message("❌ You can't adopt yourself!", ephemeral=True)

        if user.bot:
            return await interaction.response.send_message("❌ You can't adopt a bot!", ephemeral=True)

        adoption_data = get_adoption_data(user)
        if adoption_data:
            await interaction.response.send_message(f"❌ {user.mention} is already adopted by someone else!", ephemeral=True)
            return

        embed = discord.Embed(
            title="👪 Adoption Request",
            description=f"{interaction.user.mention} wants to adopt {user.mention}! 💕\n\n{user.mention}, do you accept?",
            color=discord.Color.pink()
        )
        embed.set_footer(text="You have 6 minutes to respond.")

        adopter_member = interaction.user
        if not isinstance(adopter_member, discord.Member):
            adopter_member = interaction.guild.get_member(adopter_member.id)
        if adopter_member is None:
            await interaction.response.send_message("❌ Could not find your member data in this guild.", ephemeral=True)
            return
        view = AdoptionView(adopter=adopter_member, adoptee=user)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="runaway", description="Run away from your current adopter.")
    async def _runaway(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message("This is a guild-only command!", ephemeral=True)

        member = interaction.user
        if not isinstance(member, discord.Member):
            member = interaction.guild.get_member(member.id)
        if member is None:
            await interaction.response.send_message("❌ Could not find your member data in this guild.", ephemeral=True)
            return

        adoption_data = get_adoption_data(member)
        if not adoption_data:
            await interaction.response.send_message("❌ You are not adopted by anyone!", ephemeral=True)
            return

        adopter_id = adoption_data["adopter"]
        remove_adoption(member)

        embed = discord.Embed(
            title="🏃 Runaway",
            description=f"{interaction.user.mention} has run away from their adopter (<@{adopter_id}>). 😢",
            color=discord.Color.red()
        )
        embed.set_footer(text="We hope you find happiness again.")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Marry(bot))
