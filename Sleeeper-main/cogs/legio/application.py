import discord
from discord.ext import commands
from discord import app_commands

APPLICATION_CHANNEL_ID = 1320366191763652720

QUESTIONS = [
    "What are your notable skills in-game and within a squad? ",
    "Roles you often play?",
    "And how many hours you got on squad?"
]

class ApplicationButton(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.add_item(discord.ui.Button(label="Apply", style=discord.ButtonStyle.green, custom_id="apply_button"))

    @discord.ui.button(label="Apply", style=discord.ButtonStyle.green, custom_id="apply_button")
    async def apply(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Check your DMs to start the application process!", ephemeral=True
        )
        await start_application(interaction.user, self.bot)

async def start_application(user: discord.abc.User, bot: commands.Bot):
    answers = []
    def check(m):
        return m.author.id == user.id and isinstance(m.channel, discord.DMChannel)

    try:
        user = await bot.fetch_user(user.id)
        await user.send("Hello and welcome to [LEGIO], please answer the following questions:")
        for q in QUESTIONS:
            await user.send(q)
            msg = await bot.wait_for("message", check=check, timeout=300)
            answers.append((q, msg.content))
        await user.send("Thank you! Your application has been submitted.")
        channel = bot.get_channel(APPLICATION_CHANNEL_ID)
        if isinstance(channel, discord.TextChannel):
            embed = discord.Embed(
                title="New Application",
                description=f"From: {user.mention} ({user})",
                color=discord.Color.green()
            )
            for q, a in answers:
                embed.add_field(name=q, value=a, inline=False)
            await channel.send(embed=embed)
    except Exception as e:
        try:
            user_obj = await bot.fetch_user(user.id)
            await user_obj.send("There was an error with your application or you took too long to respond.")
        except Exception:
            pass

class Application(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def application(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Apply Here!",
            description="Press the button below to start your application via DM.",
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed, view=ApplicationButton(self.bot), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Application(bot))