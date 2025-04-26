import discord
from discord.ext import commands
from discord import app_commands

BOT_VERSION = "0.5.0 Beta Build"
NEXT_VERSION = "0.5.1 Beta Build"
NEXT_VERSION_FEATURES = [
    "Add a new Feature to the AFK command",
    "Add a new Feature to the Help command",
]
RELEASE_DATE = "TBA"
NEXT_VERSION_RELEASE_DATE = "TBA"

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
        embed.add_field(name="Next Version Features", value=NEXT_VERSION_FEATURES, inline=False)
        embed.add_field(name="Next Version Release Date", value=NEXT_VERSION_RELEASE_DATE, inline=False)
        embed.add_field(name="Release Date", value=RELEASE_DATE, inline=False)
        embed.add_field(name="Support Server", value="https://discord.gg/WwApdk4z4H", inline=False)
        embed.add_field(name="Extra Info", value="**Note:** This bot is in Beta phase.", inline=False)
        embed.set_footer(text="For more information, visit the support server.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="lock_channel", description="Locks the current channel so no one can write.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lock_channel(self, interaction: discord.Interaction):
        channel = interaction.channel
        guild = interaction.guild

        overwrite = channel.overwrites_for(guild.default_role)
        overwrite.send_messages = False
        await channel.set_permissions(guild.default_role, overwrite=overwrite)

        await interaction.response.send_message(
            f"🔒 The channel {channel.mention} has been locked. Members can no longer write here."
        )

    @app_commands.command(name="unlock_channel", description="Unlocks the current channel so members can write again.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlock_channel(self, interaction: discord.Interaction):
        channel = interaction.channel
        guild = interaction.guild

        overwrite = channel.overwrites_for(guild.default_role)
        overwrite.send_messages = True
        await channel.set_permissions(guild.default_role, overwrite=overwrite)

        await interaction.response.send_message(
            f"🔓 The channel {channel.mention} has been unlocked. Members can write here again."
        )

    @app_commands.command(name="help", description="Shows a list of available commands")
    async def help_command(self, interaction: discord.Interaction):
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Support Server", url="https://discord.gg/WwApdk4z4H"))
        view.add_item(discord.ui.Button)(label="GitHub", url="https://github.com/SleeepyTPG/Sleeeper")
        await interaction.response.send_message(
            "If you need any help with my bot, join my Discord server below:", view=view
        )

async def setup(bot):
    await bot.add_cog(General(bot))