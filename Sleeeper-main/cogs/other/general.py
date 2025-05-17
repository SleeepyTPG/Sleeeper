import discord
from discord.ext import commands
from discord import app_commands

BOT_VERSION = "0.9.0 Beta Build"
NEXT_VERSION = "1.0.0 RELEASE"
RELEASE_DATE = "24.05.2025"
NEXT_VERSION_RELEASE_DATE = "17.05.2025"
LEAD_DEV = 1104736921474834493
HELPER = 1296122732173590651
SUPPORT_SERVER = "https://discord.gg/WwApdk4z4H"
GITHUB_LINK = "https://github.com/SleeepyTPG/Sleeeper"

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(label="Support Server", url=SUPPORT_SERVER, style=discord.ButtonStyle.link))
        self.add_item(discord.ui.Button(label="GitHub", url=GITHUB_LINK, style=discord.ButtonStyle.link))

class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Responds with the current latency")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! 🏓 {latency}ms")

    @app_commands.command(name="info", description="Shows information about the bot")
    async def info(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Bot Info", color=discord.Color.blue())
        embed.add_field(name="Version", value=BOT_VERSION, inline=False)
        embed.add_field(name="Release Date", value=RELEASE_DATE, inline=False)
        embed.add_field(name="Lead Dev", value=f"<@{LEAD_DEV}>", inline=False)
        embed.add_field(name="Helper", value=f"<@{HELPER}>", inline=False)
        embed.add_field(name="Support Server", value=SUPPORT_SERVER, inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="version", description="Shows the current version")
    async def version_info(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Version Info", color=discord.Color.blue())
        bot_name = self.bot.user.name if self.bot.user is not None else "Unknown"
        embed.add_field(name="Bot Name", value=bot_name, inline=False)
        embed.add_field(name="Version", value=BOT_VERSION, inline=False)
        embed.add_field(name="Next Version", value=NEXT_VERSION, inline=False)
        embed.add_field(name="Next Version Features", value="Automod Feature\n-# (v1.0.0 RELEASE)", inline=False)
        embed.add_field(name="Next Version Release Date", value=NEXT_VERSION_RELEASE_DATE, inline=False)
        embed.add_field(name="Release Date", value=RELEASE_DATE, inline=False)
        embed.add_field(name="Support Server", value=SUPPORT_SERVER, inline=False)
        embed.add_field(name="Extra Info", value="**Note:** This bot is in its Beta phase.\nIt might have Bugs!", inline=False)
        embed.set_footer(text="For more information, visit the support server.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="Get help with the bot")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Help",
            description="Need help? Use the buttons below to join our support server or visit the GitHub repository.",
            color=discord.Color.blue()
        )
        embed.set_footer(text="If you have any questions, feel free to ask in the support server.")
        await interaction.response.send_message(embed=embed, view=HelpView())

    @app_commands.command(name="servers", description="Shows the list of servers the bot is in.")
    async def servers(self, interaction: discord.Interaction):
        ALLOWED_USERS = {LEAD_DEV, HELPER}
        if interaction.user.id not in ALLOWED_USERS:
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        guilds = self.bot.guilds
        embed = discord.Embed(
            title="📜 Servers List",
            description=f"The bot is currently in **{len(guilds)}** servers:",
            color=discord.Color.blue()
        )

        if len(guilds) < 25:
            for guild in guilds:
                embed.add_field(
                    name=guild.name,
                    value=f"ID: {guild.id}\nMembers: {guild.member_count}",
                    inline=False
                )
        else:
            embed.add_field(
                name="Im in too many servers lol",
                value="Cannot display all servers due to Discord limitations.",
                inline=False
            )

        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))