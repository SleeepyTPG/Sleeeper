import random
import discord
from discord.ext import commands
from discord import app_commands


class EightBall(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="8ball", description="Ask the magic 8-ball a question!")
    @app_commands.describe(question="The question you want to ask the magic 8-ball")
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        answers = [
            "It is certain.",
            "Without a doubt.",
            "You may rely on it.",
            "Yes, definitely.",
            "It is decidedly so.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful."
        ]

        response = random.choice(answers)

        embed = discord.Embed(
            title="🎱 The Magic 8-Ball",
            description=f"**Question:** {question}\n**Answer:** {response}",
            color=discord.Color.purple()
        )
        embed.set_footer(text=f"Asked by {interaction.user.display_name}")

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(EightBall(bot))
