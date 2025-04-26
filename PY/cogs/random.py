import discord
from discord.ext import commands
from discord import app_commands
import random

marriages = {}

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

        marriages[self.proposer.id] = self.proposee.id
        marriages[self.proposee.id] = self.proposer.id

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

class Random(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roast", description="Roast another user!")
    @app_commands.describe(user="The user you want to roast")
    async def roast(self, interaction: discord.Interaction, user: discord.Member):
        if user == interaction.user:
            await interaction.response.send_message("🔥 You can't roast yourself! But nice try. 😉", ephemeral=True)
            return

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
            "You're like a pop-up ad—annoying and unnecessary.",
            "You have something on your chin… no, the third one down.",
            "You're like a cloud storage service—full of useless stuff.",
            "You're like a software update—nobody asked for you, and you make everything worse.",
            "You're like a sandwich with no filling—completely pointless.",
            "You're like a selfie stick—nobody really needs you.",
            "You're like a broken clock—wrong all the time.",
            "You're like a pencil with no lead—completely pointless.",
            "You're like a Wi-Fi password—nobody remembers you.",
            "You're like a flat tire—completely deflating.",
            "You're like a backup file—nobody remembers you exist until there's a problem.",
            "You're like a CAPTCHA test—annoying and unnecessary.",
            "You're like a bad haircut—everyone notices, but nobody says anything.",
            "You're like a knock-off brand—cheap and disappointing.",
            "You're like a bad joke—nobody laughs, but everyone remembers.",
            "You're like a low battery warning—annoying and hard to ignore.",
            "You're like a bad Wi-Fi connection—nobody wants to deal with you.",
            "You're like a pop quiz—nobody likes you, and you ruin everyone's day.",
            "You're like a spam email—unwanted and ignored.",
            "You're like a bad movie—forgettable and a waste of time.",
            "You're like a bad meme—nobody shares you, and everyone forgets you.",
            "You're like a slow internet connection—frustrating and useless.",
            "You're like a bad app—nobody downloads you, and everyone deletes you.",
            "You're like a broken light bulb—completely useless.",
            "You're like a bad review—nobody wants to see you, but everyone remembers you.",
        ]

        roast_message = random.choice(roasts)

        embed = discord.Embed(
            title="🔥 Roast Generator",
            description=f"{user.mention}, here's your roast:\n\n**{roast_message}**",
            color=discord.Color.orange()
        )
        embed.set_footer(text=f"Roasted by {interaction.user.display_name}")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Random(bot))