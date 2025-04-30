import discord
from discord.ext import commands
from discord import app_commands
import random


class Roast(commands.Cog):
    def __init__(self, bot: commands.Bot):
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


async def setup(bot: commands.Bot):
    await bot.add_cog(Roast(bot))
