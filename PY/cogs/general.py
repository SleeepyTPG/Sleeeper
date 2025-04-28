import discord
from discord.ext import commands
from discord import app_commands

BOT_VERSION = "0.5.4 Beta Build"
NEXT_VERSION = "0.5.5 Beta Build"
RELEASE_DATE = "TBA"
NEXT_VERSION_RELEASE_DATE = "02.05.2025"

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Responds with the current latency")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! 🏓 {latency}ms")

    @app_commands.command(name="info", description="Shows information about the bot")
    async def info(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Bot Info", color=discord.Color.blue())
        embed.add_field(name="Version", value=BOT_VERSION, inline=False)
        embed.add_field(name="Lead Dev", value="<@1104736921474834493>", inline=False)
        embed.add_field(name="Helper", value="<@1296122732173590651>", inline=False)
        embed.add_field(name="Support Server", value="https://discord.gg/WwApdk4z4H", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="version", description="Shows the current version")
    async def version_info(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Version Info", color=discord.Color.blue())
        embed.add_field(name="Bot Name", value=self.bot.user.name, inline=False)
        embed.add_field(name="Version", value=BOT_VERSION, inline=False)
        embed.add_field(name="Next Version", value=NEXT_VERSION, inline=False)
        embed.add_field(name="Next Version Features", value="Make the /warn more customizable", inline=False)
        embed.add_field(name="Next Version Release Date", value=NEXT_VERSION_RELEASE_DATE, inline=False)
        embed.add_field(name="Release Date", value=RELEASE_DATE, inline=False)
        embed.add_field(name="Support Server", value="https://discord.gg/WwApdk4z4H", inline=False)
        embed.add_field(name="Extra Info", value="**Note:** This bot is in Beta phase.", inline=False)
        embed.set_footer(text="For more information, visit the support server.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="Get help with the bot")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Help",
            description="Need help? Join our support server or check out the GitHub repository.",
            color=discord.Color.blue()
        )
        embed.add_field(name="Support Server", value="https://discord.gg/WwApdk4z4H", inline=False)
        embed.add_field(name="GitHub", value="https://github.com/SleeepyTPG/Sleeeper", inline=False)
        embed.set_footer(text="If you have any questions, feel free to ask in the support server.")
        
    @app_commands.command(name="servers", description="Shows the list of servers the bot is in.")
    async def servers(self, interaction: discord.Interaction):
        guilds = self.bot.guilds
        embed = discord.Embed(
            title="📜 Servers List",
            description=f"The bot is currently in **{len(guilds)}** servers:",
            color=discord.Color.blue()
        )

        for guild in guilds:
            embed.add_field(
                name=guild.name,
                value=f"ID: {guild.id}\nMembers: {guild.member_count}",
                inline=False
            )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))